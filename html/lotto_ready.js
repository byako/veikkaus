function loadResults()
{
    var xmlhttp;

    if (! game in games) {
        console.log("loadResults: game is not supported: " + game);
        return;
    }
    console.log("fetching results for game " + game);
    // initialize d1 & d2
    for (var i=1; i <= games[game].numbersLimit; i++) {
        d1.push(new Array(i,0));
        d2.push(new Array(i,0));
    }
    console.log("d1 has " + d1.length + " elements");
    if (window.XMLHttpRequest) {
        xmlhttp=new XMLHttpRequest();
    } else {
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function() {
        if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            var parseResult = JSON.parse(xmlhttp.responseText);
            if (parseResult == undefined) {
                console.log("Could not parse results data received from server");
                return;
            }
            results = parseResult;
            console.log("Got " + results.length + " results for " + game + ", parsing...");
            processResults();
            adjustHeight();
        }
    }

    xmlhttp.open("GET","latest_" + game + ".json",true);
    xmlhttp.send();
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
} 

function loadCookies() {
    var mcookie = getCookie("histLength");
    if (mcookie != "") histLength = parseInt(mcookie);
    mcookie = getCookie("showFields");
    if (mcookie != "") {
        showFields = parseInt(mcookie);
        var chkbx = document.getElementById("showFieldsCheckbox");
        if (chkbx) {
            if (showFields == 1)
                chkbx.checked = True;
            else
                chkbx.checked = False;
        }
        renderFields();
    }
}

function adjustHeight() {
    var tdiv = document.getElementById("_oldResultsTable_");
    tdiv.tBodies[0].style.height = "" + window.innerHeight - 400 + "px";
}

$(document).ready(function() {
    loadCookies();
    loadResults();
    window.addEventListener("keydown", function(e) {
        // space and arrow keys
        if([32, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
            if (e.keyCode == 38) {
                prevResultShow();
            } else if (e.keyCode == 40) {
                nextResultShow();
            }
            e.preventDefault();
        }
    }, false);
});
