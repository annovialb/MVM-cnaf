import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys

# If modifying these scopes, delete the file token.pickle.

# The ID and range of a sample spreadsheet.



def colnum_string(n):
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def insert_single_cell(row, column, text, service,SAMPLE_SPREADSHEET_ID ):

    colnum_str = colnum_string(column+1)
    row_insert = row+1
    body = {'values': [[text]]}
    range_insert = '20200412 ISO!'+colnum_str+str(row_insert)+":"+colnum_str+str(row_insert)

    print ("Inserting ",text , " in rage", range_insert )
    
    result = service.spreadsheets().values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
        range=range_insert,
        valueInputOption="RAW",
        body=body).execute()

def initGsheet(SAMPLE_SPREADSHEET_ID):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    return service

def getSheetNames(service,SAMPLE_SPREADSHEET_ID):
    sheet = service.spreadsheets()
    sheet_metadata = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', '')
    names = []
    for i in sheets:
        names.append(i.get("properties", {}).get("title", 0))
    return names


def getRange(service,SAMPLE_SPREADSHEET_ID, SAMPLE_RANGE_NAME ):
    sheet = service.spreadsheets()

    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])
    return values


def getIDsFromSheet(SAMPLE_SPREADSHEET_ID,Suffix_SAMPLE_RANGE_NAME, service, sheet_name, VERB=True):

    
    col_simulator_filename = {}
    col_mvm_filename={}
    col_campaign = {}
    dict_ids = {}
    s = sheet_name
    
    SAMPLE_RANGE_NAME = s+Suffix_SAMPLE_RANGE_NAME
    if (VERB==True):
            print ("----------Studying SHEET", s)
    values = getRange(service,SAMPLE_SPREADSHEET_ID,SAMPLE_RANGE_NAME )
    if not values:
            if (VERB==True):
                print('No data found in Sheet, skipping ....',s)
                return (False, False, False, False)

    num=0
    headers = []
    col_simulator_filename=-1
    col_mvm_filename=-1
    col_campaign=-1
    dict_id = {}
    for row in range(0,len(values)):
#            print (row)
            num=num+1
            if num <= 2 :
                #this is the ISO requirement line, it MUST be here
                continue
            if num ==3 :
                for col in range(0,len(values[row])):
                    headers.append(values[row][col])
                    if values[row][col] == "simulator_filename":
                        col_simulator_filename = col
                    if values[row][col] == "MVM_filename":
                        col_mvm_filename = col
                    if values[row][col] == "campaign":
                        col_campaign = col
                continue
            if values[row][0]  == "":
                if (VERB==True):
                        print ("Skipping empty line")
                continue

            #        print (col_simulator_filename[s], col_mvm_filename[s] )
            if col_simulator_filename ==-1 or col_mvm_filename==-1 or col_campaign==-1:
                if (VERB==True):
                    print ("Skipping sheet",s, ", does not contain filename or campaign columns")
                return (False, False, False, False, False)
#
# check if all the colums have at least the length       
#
            if (len(values[row])<col_simulator_filename or len(values[row])<col_mvm_filename or len(values[row])<col_campaign ):
               if (VERB==True):
                 print ("ROW malformed (too short)")
               continue

#
# ifthere is no campaign, go away
#
            if (values[row][col_campaign] == ""):
                   if (VERB==True):
                     print ("Campaign not defined for ID",values[row][0])
                   continue

            if (values[row][col_simulator_filename]== "" or values[row][col_mvm_filename]==""):
                if (VERB==True):
                    print ("*  ID ", s, values[row][0], " Campaign",(values[row][col_campaign] ))
#                    print('%s %s %s %s' % ("* ID ", s, values[row][0], " Campaign",values[row][col_campaign[s]] ))
                dict_id[(values[row][0],values[row][col_campaign])] =(row,False)
            else:
                if (VERB==True):
                    print ("  ID ", s, values[row][0], " Campaign",(values[row][col_campaign] ))
#                    print('%s %s %s %s' % ("  ID ", s, values[row][0], " Campaign",(values[row][col_campaign[s]] )))
                    
                dict_id[(values[row][0],values[row][col_campaign])] =(row,True)
    return   (dict_id,col_simulator_filename,col_mvm_filename,col_campaign, values)


def getIDsFromMultipleSheets(SAMPLE_SPREADSHEET_ID,Suffix_SAMPLE_RANGE_NAME, service,VERB=True):

    sheet_names = getSheetNames(service,SAMPLE_SPREADSHEET_ID)

    dict_ids = {}
    col_simulator_filenames = {}
    col_mvm_filenames = {}
    col_campaigns = {}
    all_s = {}
    for s in sheet_names:
        if (VERB==True):
            print ("----------Studying SHEET", s)
        (dict_id,col_simulator_filename,col_mvm_filename,col_campaign, all) = getIDsFromSheet(SAMPLE_SPREADSHEET_ID,Suffix_SAMPLE_RANGE_NAME, service, s, VERB)
        dict_ids[s] = dict_id
        col_simulator_filenames[s]=col_simulator_filename
        col_mvm_filenames[s]=col_mvm_filename
        col_campaigns[s]= col_campaign
        all_s[s]= all

    return (dict_ids,col_simulator_filenames,col_mvm_filenames,col_campaigns, all_s)

def getIDsForm(SAMPLE_SPREADSHEET_ID,Suffix_SAMPLE_RANGE_NAME,service, VERB=True):
    
    (dict_ids,col_simulator_filenames,col_mvm_filenames,col_campaigns, all_s) = getIDsFromMultipleSheets(SAMPLE_SPREADSHEET_ID,Suffix_SAMPLE_RANGE_NAME, service,VERB)
    # I need to define options as a map
    optionmap = {}
    for site in dict_ids.keys():
        if (VERB==True):
            print ("Key ",site)
            print (dict_ids[site].values())
        optionmap[site]={}
        for key in  dict_ids[site]:
            value = dict_ids[site][key]
            campaign = key[1]
            id=key[0]
            filled=value[1]
            if (VERB==True):
                print ("Global ID ",id, campaign, "is it filled? " ,filled)
            if campaign not in optionmap[site]:
                optionmap[site][campaign]={}
            optionmap[site][campaign][id]=filled

    optionmapFILLED={}
    optionmapUNFILLED={}
    for s1 in optionmap:
        site = s1
        rest1 = optionmap[site]
        for s2 in rest1:
            campaign = s2
            rest2 = optionmap[site][campaign]
            for s3 in rest2:
                id = s3
                filled = optionmap[site][campaign][id]
                if filled == True:
                    if site not in optionmapFILLED:
                        optionmapFILLED[site] = {}
                    if campaign not in optionmapFILLED[site]:
                        optionmapFILLED[site][campaign]=[]
                    optionmapFILLED[site][campaign].append(id)
                if filled == False:
                    if site not in optionmapUNFILLED:
                        optionmapUNFILLED[site] = {}
                    if campaign not in optionmapUNFILLED[site]:
                        optionmapUNFILLED[site][campaign]=[]
                    optionmapUNFILLED[site][campaign].append(id)
            
            
    return (optionmap, optionmapFILLED,optionmapUNFILLED)


            
