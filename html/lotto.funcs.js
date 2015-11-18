numbersSelected = []; // initially empty, holds numbers selected by user
coverage = 1; // calculated based on length of "numbersSelected"

var roundsCounter = 0;
var selectedRound = 0;

roundResults = new Array();

logsList = new Array();

// d1 : total times a number has appeared
var d1 = new Array();

// d2: number times a number has appeared as an additional
var d2 = new Array();
// d3: the average number from d1
var d3 = [ [1,0], [39,0] ];
// d4: the minimum number from d1
var d4 = [ [1,0], [39,0] ];
// d5: the maximum number from d1 
var d5 = [ [1,0], [39,0] ];
// d6: number of times number has appeared by round
d6 = new Array();

function setMinAvgMax() {
	var avg1 = 0;
	var min1 = 1000;
	var max1 = 0;

	for (var i=0; i<39; i++) {
		if (d1[i][1] > max1) max1 = d1[i][1];
		if (d1[i][1] < min1) min1 = d1[i][1];
		avg1 += d1[i][1];
	}
	avg1 /= 39;

	d3[0][1] = avg1;
	d3[1][1] = avg1;
	d4[0][1] = min1;
	d4[1][1] = min1;
	d5[0][1] = max1;
	d5[1][1] = max1;

}

var statsPlot;
function plotStatsN(toPlot) {
	alert("plotting : " + toPlot);
	statsPlot = $.plot($("#_stats_"), [ toPlot ], { xaxis: { ticks:[
		1,2,3,4,5,6,7,8,9,10,
		11,12,13,14,15,16,17,18,19,20,
		21,22,23,24,25,26,27,28,29,30,
		31,32,33,34,35,36,37,38,39
		]} }
	);
};

function processStats() {
	var table_ = document.getElementById("_oldResultsTable_");
	if (table_) {
		table_.onclick = function(e) {
			var target = (e || window.event).target;
			fieldsShowRound(target.roundNumber);
			plotStatsN(d6[target.roundNumber-1]);
		}
		for (var i=0; i < roundsCounter; i++) {
			var row_ = table_.insertRow(i);
			row_.id = "orRow" + i;
			roundResults[i].numbers.sort();
			for (j=1; j<40; j++) {
				var cell_ = row_.insertCell(j-1);
				if (roundResults[i].indexOf('' + j) >= 0) {
					cell_.innerHTML=String(j);
				}
				cell_.width="20px";
				cell_.height="20px";
				cell_.roundNumber=i;
				cell_.style.textAlign="center";
			}
		}
	}
}

function addNavDivs() {
	for (i=0;i < roundsCounter;i++) {
		$("#roundNav").append("<div class='nav' id='l"+i+"' onmouseover='updateLog(event)'>"+i+"</div>");
//		$("#sliderDiv").append("<div class='navBar' id='l"+i+"' onmouseover='updateLog(event)'></div>");
	}
}

function increaseHeight(id) {
	var element = document.getElementById(id);
	if (element) {
		var curH = Number(element.style.height.replace("px",""));
		if (curH < 1000) {
			element.style.height = String((curH+50) + "px");
		} else {
			alert("isn't it too big?");
		}
	} else {
		alert("didn't find element:" + id);
	}
}

function decreaseHeight(id) {
	var element = document.getElementById(id);
	if (element) {
		var curH = Number(element.style.height.replace("px",""));
		if (curH > 150) {
			element.style.height = String((curH-50) + "px");
		} else {
			alert("it's minimal already");
		}
	} else {
		alert("didn't find element:" + id);
	}
}

function updateLog(e) {
	temp_ = window[e.target.id];
	min_ = 1000;
	max_ = 0;
	sum_ = 0;
	for (i=0;i<39;i++) {
		if (temp_[i][1] > max_) max_ = temp_[i][1];
		if (temp_[i][1] < min_) min_ = temp_[i][1];
		sum_ += temp_[i][1];
	}
	avg_ = sum_ / 39;
	$.plot($("#_logs_"), [window[e.target.id],[[0,min_],[39,min_]],[[0,max_],[39,max_]],[[0,avg_],[39,avg_]]
        ], { xaxis: { ticks:[
                1,2,3,4,5,6,7,8,9,10,
                11,12,13,14,15,16,17,18,19,20,
                21,22,23,24,25,26,27,28,29,30,
                31,32,33,34,35,36,37,38,39
        ]} }
        );
}

function addFields() {
	var table_ = document.getElementById("fieldsTable");
	if (table_) {
		var rows_ = Array();

		for (var i=0; i<7; i++) {
			rows_[i] = table_.insertRow(i);
		}

		for (var i=0; i<6; i++) {
			for (var j=0;j<7;j++) {
				if (i > 2 && j == 6) break;
				var cell_ = rows_[j].insertCell(i);
				var idx= 1 + i + j*6;
				cell_.id = "cell" + String(idx);
				cell_.width="20px";
				cell_.height="20px";
				cell_.selected = false;
				cell_.style.textAlign="center";
				cell_.innerHTML=String(i+1+j*6);
			}
		}
	}
}

function selectNumber(e) {
	var target = (e || window.event).target;
	if (target.tagName in {TD:1, TH:1}) {
		var newNumber = Number(target.innerHTML);
		if (target.selected == false) {
			document.getElementById("cell" + newNumber).selected = true;
			if (document.getElementById("cell" + newNumber).style.backgroundColor == "#fff" ){
				document.getElementById("cell" + newNumber).style.backgroundColor = "#AAFFAA";
			} else {
				document.getElementById("cell" + newNumber).style.backgroundColor = "#386";
			}
			target.selected = true;
	        target.setAttribute('style', 'background-color: #386');
			numbersSelected.push(newNumber);
			var newLength = numbersSelected.length;
			if (newLength > 7) {
				coverage = coverage * newLength / (newLength - 7);
			} else {
				coverage = 1;
			}
		} else {
			document.getElementById("cell" + newNumber).selected = false;
			if (document.getElementById("cell" + newNumber).style.backgroundColor == "#AAFFAA" ){
				document.getElementById("cell" + newNumber).style.backgroundColor = "#fff";
			} else {
				document.getElementById("cell" + newNumber).style.backgroundColor =  document.getElementsByTagName('body')[0].style.backgroundColor;
			}
			target.selected = false;
			target.style.backgroundColor = document.getElementsByTagName('body')[0].style.backgroundColor;
			var i = numbersSelected.indexOf(newNumber);
			numbersSelected.splice(i,1);
			var newLength = numbersSelected.length;
			if (newLength > 7) {
				coverage = coverage * (newLength - 6) /( newLength + 1);
			} else {
				coverage = 1;
			}
		}
		document.getElementById("coverageDiv").innerHTML = coverage;
		if (numbersSelected.length == 7) {
			searchStr = numbersSelected.join();
			document.getElementById("combInput").value=searchStr;
			checkCombination();
		}
	}
};


function checkCombination() {
	combInput = document.getElementById("combInput");
	inputs = combInput.value.split(",");
	if (inputs.length != 7) {
		alert("Incorrect format. Please, enter 7 numbers separated by comma.");
		document.getElementById("checkDiv").style.backgroundColor="#AA1010";
		return;
	}
	for (var i=0;i<7;i++) {
		el = parseInt(inputs[i]);
		if (el < 0 || el > 39) {
			alert("Incorrect format. Please, enter 7 numbers separated by comma.");
			document.getElementById("checkDiv").style.backgroundColor="#AA1010";
			return;
		}
	}
	document.getElementById('checkDiv').style.backgroundColor = document.getElementsByTagName('body')[0].style.backgroundColor;
	for (var i=0; i<roundResults.length; i++) {
		res=1;
		for (var j=0;j<7;j++){
			if (roundResults[i].indexOf(inputs[j]) < 0) {
				res = 0;
				break;
			}
		}
		if (res == 1) { // we found full match
			document.getElementById("checkDiv").style.backgroundColor="#10AA10";
			fieldsShowRound(i);
			break;
		}
	}
}

function fieldsShowRound(roundNumber) {
	if (roundNumber > roundResults.length || roundNumber < 0) return;
	// paint back already selected cells to body's bg color

	if (selectedRound >= 0) {
		for (var i=0; i<roundResults[selectedRound].length; i++) {
			var cell_ = document.getElementById("cell" + String(roundResults[selectedRound][i]));
			if (cell_) {
				cell_.style.backgroundColor=document.getElementsByTagName('body')[0].style.backgroundColor;
				cell_.style.color=document.getElementsByTagName('body')[0].style.color;
			}
		}

		var tr_ = document.getElementById("orRow" + selectedRound);
		if (tr_) {
			tr_.style.backgroundColor = document.getElementsByTagName('body')[0].style.backgroundColor;
			tr_.style.color = document.getElementsByTagName('body')[0].style.color;
		}
	}

	if (roundNumber == selectedRound) {
		selectedRound = -1;
		return;
	}

	for (var i=0;i<roundResults[roundNumber].length;i++) {
		var cell_ = document.getElementById("cell" + String(roundResults[roundNumber][i]));
		if (cell_) {
			if (cell_.selected == true) {
				cell_.style.backgroundColor="#AAFFAA";
			} else {
				cell_.style.backgroundColor="#fff";
			}
			cell_.style.color="#000";
		}
	}
	tr_ = document.getElementById("orRow" + roundNumber);
	if (tr_) {
		tr_.style.backgroundColor = "#fff";
		tr_.style.color = "#000";
	}
	selectedRound=roundNumber;
} 

function fieldsShowStats() {
	var table_ = document.getElementById("fieldsTable");
	if (table_) {
		for (var idx=1; idx<40; idx++) {
				var cell_ = document.getElementById("cell" + String(idx));
				var color_ = (d3[1][1]-d1[idx-1][1]);
				var colorText = "";
				if (color_ > 0) { // cold colors
					colorText = "rgb(" + 128 + "," + 128 + "," + (64+color_*10) + ")";
				} else if (color_ < 0) { // hot colors
					colorText = "rgb(" + (128+Math.abs(color_*5)) + "," + (128+Math.abs(color_*5)) + "," + 0 + ")";
				} else { // neutral colors
					colorText = "#808080"
				}
				cell_.style.backgroundColor = colorText;
		}
	}
}

function populateOldResultsStats() {
	var table_ = document.getElementById("_oldResultsStatsTable_");
	if (table_) {
		table_.onclick = selectNumber;
		var rows_ = Array();
		for (var i=0; i<4; i++) {
			rows_[i] = table_.insertRow(i);
		}
		var cell_ = rows_[1].insertCell(0);
		cell_.height="25px";
		for (var i=0; i<39; i++) {
			cell_ = rows_[0].insertCell(i);
			cell_.id = "oldResultsStatsCell" + String(i+1);
			cell_.style.textAlign="center";
			cell_.innerHTML=String(i+1);
			cell_.selected = false;

			cell_ = rows_[2].insertCell(i);
			cell_.style.textAlign="center";
			cell_.innerHTML=String(d1[i][1]);

			cell_ = rows_[3].insertCell(i);
			cell_.style.textAlign="center";
			cell_.innerHTML=String(d2[i][1]);
		}
	}
	document.getElementById("avgDiv").innerHTML = '' + d3[0][1].toFixed(0);
	document.getElementById("minDiv").innerHTML = '' + d4[0][1].toFixed(0);
	document.getElementById("maxDiv").innerHTML = '' + d5[0][1].toFixed(0);
}

        
function showLog(element) {
	var div_ = document.getElementById("_oldResults_");
	var plus_ = document.getElementById("logPlus");
	var minus_ = document.getElementById("logMinus");
	if (!element.checked) {
		div_.style.visibility = "hidden";
		div_.style.display = "none";
		plus_.disabled = true;
		minus_.disabled = true;
	} else {
		div_.style.visibility = "visible";
		div_.style.display = "block";
		plus_.disabled = false;
		minus_.disabled = false;
	}
}
        
function showStatsGraph(element) {
	var div_ = document.getElementById("_logs_");
	var div_2 = document.getElementById("roundNav");
	var plus_ = document.getElementById("statsGraphPlus");
	var minus_ = document.getElementById("statsGraphMinus");
	var iframe_div = document.getElementById("iframe1");
	if (!element.checked) {
		div_.style.visibility = "hidden";
		div_.style.display = "none";
		div_2.style.visibility = "hidden";
		div_2.style.display = "none";
		iframe_div.height="500px";
		plus_.disabled = true;
		minus_.disabled = true;
	} else {
		div_.style.visibility = "visible";
		div_.style.display = "block";
		div_2.style.visibility = "visible";
		div_2.style.display = "block";
		iframe_div.height="100px";
		plus_.disabled = false;
		minus_.disabled = false;
	}
}
        
function showStats(element) {
	var div_ = document.getElementById("_stats_");
	var plus_ = document.getElementById("statsPlus");
	var minus_ = document.getElementById("statsMinus");
	if (!element.checked) {
		div_.style.visibility = "hidden";
		div_.style.display = "none";
		plus_.disabled = true;
		minus_.disabled = true;
	} else {
		div_.style.visibility = "visible";
		div_.style.display = "block";
		plus_.disabled = false;
		minus_.disabled = false;
	}
}
        
function showFields(element) {
	var div_ = document.getElementById("fieldsTable");
	var plus_ = document.getElementById("fieldsPlus");
	var minus_ = document.getElementById("fieldsMinus");
	if (!element.checked) {
		div_.style.visibility = "hidden";
		div_.style.display = "none";
		plus_.disabled = true;
		minus_.disabled = true;
	} else {
		div_.style.visibility = "visible";
		div_.style.display = "block";
		plus_.disabled = false;
		minus_.disabled = false;
	}
}

