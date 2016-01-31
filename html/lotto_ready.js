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
            var parseResult = JSON.parse("[" + xmlhttp.responseText + "{}]");
            if (parseResult == undefined) {
                console.log("Could not parse results data received from server");
                return;
            }
            results = parseResult;
            console.log("Got " + results.length + " results for " + game + ", parting...");
            processResults();
        }
    }

    xmlhttp.open("GET","latest_" + game + ".json",true);
    xmlhttp.send();
}


$(document).ready(function() {
   loadResults();
});
