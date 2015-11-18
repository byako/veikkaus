function loadResults()
{
	var xmlhttp;
	var resCounter = new Array();
	var resAddCounter = new Array();
	// initialize d1 & d2
	for (var i=1; i<40; i++) {
		d1.push(new Array(i,0));
		d2.push(new Array(i,0));
	}
	if (window.XMLHttpRequest) {
		xmlhttp=new XMLHttpRequest();
	} else {
		xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
	}
	roundsCounter = 0;
	xmlhttp.onreadystatechange=function() {
		if (xmlhttp.readyState==4 && xmlhttp.status==200) {
			var parsedResults= JSON.parse("[" + xmlhttp.responseText + "{}]");
			if (parsedResults == undefined) {
				return;
			}
			roundsCounter = parsedResults.length - 1;
			for (var i=0; i < roundsCounter; i++) {
				var parts = parsedResults[i].split(",");
				var mains = parts[3].replace(/^\s+/,"").replace(/\s+$/,"").split(/\s+/);
				var adds = parts[5].replace(/^\s+/,"").replace(/\s+$/,"").split(/\s+/);

				// add main appearances
				for (var j=0; j < parsedResults[i].numbers.length; j++) {
					main = parsedResults[i].numbers[j];
					d1[main-1][1] = d1[main-1][1] + 1;
				}
				for (var j=0; j < parsedResults[i].adds.length; j++) {
					addit = parsedResults[i].adds[j];
					d1[addit-1][1] = d1[addit-1][1] + 1;
					d2[addit-1][1] = d2[addit-1][1] + 1;
				}
				roundResults.push(mains.concat(adds));
				d6.push(d1.slice(0));
			}
			processStats();
			setMinAvgMax();
			addFields();
			fieldsShowRound(roundsCounter - 1);
			populateOldResultsStats();
		}
	}

	xmlhttp.open("GET","latest.json",true);
	xmlhttp.send();
}

$(document).ready(function() {
	loadResults();
//	addNavDivs();
//	fieldsShowStats()
});
