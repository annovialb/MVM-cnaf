function validateForm() {
    var f1=document.forms["uploadForm"]["file1"].value;
    if(f1=="") {
        alert("Need to provide a file1");
        return false;
    }
    return true;
}

function updateCampaign() {
    var y = document.getElementById("selectTestSite").selectedIndex;
    document.getElementById("selectCampaign").innerHTML = opts_Campaign[y];
}

function updateTestID() {
    var x = document.getElementById("selectTestSite").selectedIndex;
    var y = document.getElementById("selectCampaign").selectedIndex;
    document.getElementById("selectTestID").innerHTML = opts_TestID[x][y];
}

