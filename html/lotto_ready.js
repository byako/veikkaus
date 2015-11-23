function loadResults()
{
    var xmlhttp;
    var resCounter = [];
    var resAddCounter = [];

    if (game != "EJACKPOT" && game != "LOTTO") {
        return;
    }

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
    roundsCounter = 0;
    xmlhttp.onreadystatechange=function() {
        if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            results= JSON.parse("[" + xmlhttp.responseText + "{}]");
            if (results == undefined) {
                return;
            }
            roundsCounter = results.length - 1;
            for (var i=0; i < roundsCounter; i++) {
                // add main appearances
                for (var j=0; j < results[i].numbers.length; j++) {
                    var main = results[i].numbers[j];
                    d1[main-1][1] = d1[main-1][1] + 1;
                }
                for (var j=0; j < results[i].adds.length; j++) {
                    var addit = results[i].adds[j];
                    d1[addit-1][1] = d1[addit-1][1] + 1;
                    d2[addit-1][1] = d2[addit-1][1] + 1;
                }
                d6.push(d1.slice(0));
            }
            processStats();
            setMinAvgMax();
            addFields();
            fieldsShowRound(roundsCounter - 1);
            populateOldResultsStats();
        }
    }

    xmlhttp.open("GET","latest_" + game + ".json",true);
    xmlhttp.send();
}

$(document).ready(function() {
    loadResults();
});
