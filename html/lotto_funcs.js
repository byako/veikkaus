var numbersSelected = []; // initially empty, holds numbers selected by user
var coverage = 1; // calculated based on length of "numbersSelected"

var roundsCounter = 0;
var selectedRound = 0;

var game = "EJACKPOT";
var games = {
    "EJACKPOT": {
        "fieldsRows":9,
        "fieldsColumns":6,
        "drawNumbersLimit":5,
        "additionalLimit":2,
        "numbersStart":1,
        "numbersLimit":50,
        "additionalNumbersStart":1,
        "additionalNumbersLimit":10,
    },
    "LOTTO": {
        "fieldsRows":6,
        "fieldsColumns":7,
        "drawNumbers":5,
        "drawAdditional":2,
        "numbersStart":1,
        "numbersLimit":39,
        "additionalNumbersStart":1,
        "additionalNumbersLimit":39,
    }
}

var results = [];

var logsList = [];

// d1 : total times a number has appeared
var d1 = [];

// d2: number times a number has appeared as an additional
var d2 = [];
// d3: the average number from d1
var d3 = [ [1,0], [2,0] ];
// d4: the minimum number from d1
var d4 = [ [1,0], [2,0] ];
// d5: the maximum number from d1 
var d5 = [ [1,0], [2,0] ];
// d6: number of times number has appeared by round
var d6 = [];

function setMinAvgMax() {
    var avg1 = 0;
    var min1 = 1000;
    var max1 = 0;

    for (var i=0; i<games[game].numbersLimit; i++) {
        if (d1[i][1] > max1) max1 = d1[i][1];
        if (d1[i][1] < min1) min1 = d1[i][1];
        avg1 += d1[i][1];
    }
    avg1 /= (games[game].numbersLimit);

    d3[0][1] = avg1;
    d3[1][1] = avg1;
    d4[0][1] = min1;
    d4[1][1] = min1;
    d5[0][1] = max1;
    d5[1][1] = max1;

}

function swapImage(roundNumber) {
    if (roundNumber < results.length) {
        var weekn = parseInt(results[roundNumber].week)+1;
        var yearn = results[roundNumber].year;
        // 2015_46_c.data.png
        document.getElementById("gnuplotted").setAttribute("src","png/" + yearn + "_" + weekn + "_c.data.png");
    }
}

function processStats() {
    var table_ = document.getElementById("_oldResultsTable_");
    if (table_) {
        table_.onclick = function(e) {
            var target = (e || window.event).target;
            fieldsShowRound(target.roundNumber);
            swapImage(target.roundNumber);
        }
        for (var i=0; i < roundsCounter; i++) {
            var row_ = table_.insertRow(i);
            row_.id = "orRow" + i;
            results[i].numbers.sort();
            for (j=1; j<=games[game].numbersLimit; j++) {
                var cell_ = row_.insertCell(j-1);
                if (results[i].numbers.indexOf(j) >= 0) {// || results[i].adds.indexOf(j) >= 0) {
                    cell_.innerHTML=String(j);
                }
                if (results[i].adds.indexOf(j) >= 0) {
                    cell_.style.background="#383";
                    if (game == "LOTTO") {
                        cell_.innerHTML = String(j);
                    }
                }
                cell_.width="20px";
                cell_.height="20px";
                cell_.roundNumber=i;
                cell_.style.textAlign="center";
            }
        }
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

function addFields() {
    console.log("adding fields setup");
    var table_ = document.getElementById("fieldsTable");
    if (table_) {
        var rows_ = Array();

        for (var i=0; i<games[game].fieldsRows; i++) {
            rows_[i] = table_.insertRow(i);
        }
        console.log("added " + rows_.length + " rows");
        for (var i=0; i < games[game].fieldsRows; i++) {
            for (var j=0; j < games[game].fieldsColumns; j++) {
                if (i > 2 && j == games[game].fieldsColumns) break;
                var cell_ = rows_[i].insertCell(j);
                var idx= 1 + j + i*games[game].fieldsColumns;
                if (idx > games[game].numbersLimit) break;
                cell_.id = "cell" + String(idx);
                cell_.width="20px";
                cell_.height="20px";
                cell_.selected = false;
                cell_.style.textAlign="center";
                cell_.innerHTML=String(idx);
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
/*            var newLength = numbersSelected.length;
            if (newLength >= numbersLimit) {
                coverage = coverage * newLength / (newLength - numbersLimit);
            } else {
                coverage = 1;
            }*/
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
/*            var newLength = numbersSelected.length;
            if (newLength > 7) {
                coverage = coverage * (newLength - 6) /( newLength + 1);
            } else {
                coverage = 1;
            }*/
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
    for (var i=0; i<results.length; i++) {
        res=1;
        for (var j=0;j<7;j++){
            if (results[i].numbers.indexOf(inputs[j]) < 0 && results[i].adds.indexOf(inputs[i]) < 0) {
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
    if (roundNumber > results.length || roundNumber < 0) return;
    // paint back already selected cells to body's bg color

    if (selectedRound >= 0) {
        for (var i=0; i < results[selectedRound].numbers.length; i++) {
            var cell_ = document.getElementById("cell" + String(results[selectedRound].numbers[i]));
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

    for (var i=0; i < results[roundNumber].numbers.length;i++) {
        var cell_ = document.getElementById("cell" + String(results[roundNumber].numbers[i]));
        if (cell_) {
            if (cell_.selected == true) {
                cell_.style.backgroundColor="#AAFFAA";
            } else {
                cell_.style.backgroundColor="#fff";
            }
            cell_.style.color="#000";
        }
    }
    for (var i=0; i < results[roundNumber].adds.length;i++) {
        var cell_ = document.getElementById("cell" + String(results[roundNumber].adds[i]));
        if (cell_) {
            if (cell_.selected == true) {
                cell_.style.backgroundColor="#ffFFAA";
            } else {
                cell_.style.backgroundColor="#f99";
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
        for (var i=0; i<games[game].numbersLimit; i++) {
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

