var numbersSelected = []; // initially empty, holds numbers selected by user
var coverage = 1; // calculated based on length of "numbersSelected"
var showExtendedResultInfo = true;
var roundsCounter = 0;
var selectedRound = 0;
var showFields = 1;
var histLength = 52;
var game = "ejackpot";
var games = {
    "ejackpot": {
        "fieldsRows":9,
        "fieldsColumns":6,
        "numbers":5,
        "additionalNumbers":2,
        "numbersStart":1,
        "numbersLimit":50,
        "additionalNumbersStart":1,
        "additionalNumbersLimit":12,
        "combinationLength":7
    },
}
var gameStats = {
    "jackpotted":0,
    "moneyWonOverall":0,
    "moneyWonJackpotted":0,
    "repeatedCombinations":0,
    "jackpottedPerYear":{},
    "jackpottedPerMonth":{}
};
var results = [];
var initialized = false; // used in first highlighting
var logsList = [];

// d1 :times a number has appeared as primary
var d1 = [];

// d2: times a number has appeared as an additional
var d2 = [];
// d3: the average number from d1
var d3 = [ [1,0], [2,0] ];
// d4: the minimum number from d1
var d4 = [ [1,0], [2,0] ];
// d5: the maximum number from d1 
var d5 = [ [1,0], [2,0] ];
// d6: number of times number has appeared by round
var d6 = [];

function switchGame(gameName) {
    if (gameName in games) {
        if (game == gameName) {
            console.log("Selected current game, skipping all actions");
            return;
        }
        console.log("switching to new game: " + gameName);
        game = gameName;
        $("#switchGameButton").html(gameName + "<span class='caret'></span>");
        setCookie("game", game, 365);
        loadResults();
    } else {
        console.log("game " + gameName + " is not supported");
    }
}

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
    console.log("new image is for number: " + roundNumber);
    if (roundNumber < results.length) {
        var id = parseInt(results[roundNumber].id);
        var newURL = "png/" + game + "_id_"  + id + ".png";
        console.log("replacing picture with " + newURL);
        document.getElementById("gnuplotted").setAttribute("src", newURL);
    }
}


function drawHistory() {
    var table_ = document.getElementById("_oldResultsTable_");
    if (table_) {
        table_.innerHTML = "";
        table_.onclick = function(e) {
            var target = (e || window.event).target;
            rerender(target.roundNumber);
        }
        if (roundsCounter < histLength) {
            console.log("drawHistory: adjusting history size, it was longer than results list");
            histLength = roundsCounter;
            $("#histLengthInput").value = histLength;
        }
        var tableRows = 0;
        console.log("loading " + histLength + " results out of " + roundsCounter + " available");
        for (var i=(roundsCounter - histLength); i <= roundsCounter; i++) {
            var row_ = table_.insertRow(tableRows);
            if (row_ == undefined) {
                console.log("couldn't insert row to table");
                return;
            }
            console.log("Adding result " + results[i].id)
            tableRows++;
            row_.id = "orRow" + i;
            results[i].primary.sort();
            for (j=1; j<=games[game].numbersLimit; j++) {
                var cell_ = row_.insertCell(j-1);
                if (results[i].primary.indexOf(j) >= 0) {
                    cell_.className += "tableCellStandard";
                    cell_.innerHTML = String(j);
                } else if (results[i].adds.indexOf(j) >= 0) {
                    cell_.className += "tableCellAdditional";
                    cell_.innerHTML = String(j);
                } else {
                    cell_.className += "tableCell";
                }
                cell_.roundNumber=i;
            }
            if ("jackpot_won" in results[i] && results[i].jackpot_won === true) {
                row_.style.backgroundColor = "#807d53";
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
        table_.innerHTML = "";
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
                cell_.innerHTML="&nbsp" + String(idx) + "&nbsp";
            }
        }
    }
}

/*
 * handles table onclick event
 */
function selectNumber(e) {
    var target = (e || window.event).target;
    if (target.tagName in {TD:1, TH:1}) {
        var newNumber = Number(target.innerHTML);
        if (target.selected == false) {
            console.log("selcting number");
            document.getElementById("cell" + newNumber).selected = true;
            if (document.getElementById("cell" + newNumber).style.backgroundColor == "#fff" ) {
                document.getElementById("cell" + newNumber).style.backgroundColor = "#AAFFAA";
            } else {
                document.getElementById("cell" + newNumber).style.backgroundColor = "#386";
            }
            target.selected = true;
            target.setAttribute('style', 'background-color: #386');
            numbersSelected.push(newNumber);
        } else {
            console.log("unselcting number");
            document.getElementById("cell" + newNumber).selected = false;
            if (document.getElementById("cell" + newNumber).style.backgroundColor == "#AAFFAA" ) {
                document.getElementById("cell" + newNumber).style.backgroundColor = "#fff";
            } else {
                document.getElementById("cell" + newNumber).style.backgroundColor =  document.getElementsByTagName('body')[0].style.backgroundColor;
            }
            target.selected = false;
            target.style.backgroundColor = document.getElementsByTagName('body')[0].style.backgroundColor;
            var i = numbersSelected.indexOf(newNumber);
            numbersSelected.splice(i,1);
        }
        if (numbersSelected.length >= games[game].numbersLimit) {
            coverage = coverage * newLength / (newLength - games[game].numbersLimit);
        } else {
            coverage = 1;
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
    console.log("checking combination");
    /* get entered numbers */
    var combInput = document.getElementById("combInput");
    var inputs = combInput.value.split(",");
    if (inputs.length != games[game].combinationLength) {
        inputs = combInput.value.split(" ");
        if (inputs.length != games[game].combinationLength) {
            alert("Incorrect format. Please, enter " + games[game].combinationLength + " numbers separated by comma or space");
            document.getElementById("checkDiv").style.backgroundColor="#AA1010";
            return;
        }
    }

    /* verify entered numbers */
    for (var i=0;i<7;i++) {
        var el = parseInt(inputs[i]);
        if (el < games[game].numbersStart || el > games[game].numbersLimit) {
            alert("Incorrect format. Please, enter " + games[game].combinationLength + " numbers separated by comma or space");
            document.getElementById("checkDiv").style.backgroundColor="#AA1010";
            return;
        }
        inputs[i] = el;
    }

    document.getElementById('checkDiv').style.backgroundColor = document.getElementsByTagName('body')[0].style.backgroundColor;
    for (var i=0; i<results.length-1; i++) {
        var res=1;
        for (var j=0;j<7;j++) {
            if (results[i].primary.indexOf(inputs[j]) < 0 && results[i].adds.indexOf(inputs[j]) < 0) {
                res = 0;
                break;
            }
        }
        if (res == 1) { // we found full match
            document.getElementById("checkDiv").style.backgroundColor="#10AA10";
            rerender(i);
            break;
        }
    }
}

/* handle clicking on the old results : highlighting it, etc. */
function fieldsShowRound(roundNumber) {
    if (roundNumber == selectedRound) {
        if (initialized === false) {
            initialized = true;
        } else {
            console.log("Not highlighting already selected round");
            return;
        }
    } else if (roundNumber > results.length || roundNumber < 0) {
        console.error("Cannot rerender round number " + roundNumber);
        return;
    }
    // paint back already selected cells to body's bg color
    console.log("roundNumber: " + roundNumber + ", selectedRound: " + selectedRound);
    if (selectedRound >= 0 && selectedRound <= roundsCounter) {
        console.log("highlighting result " + roundNumber);
        for (var i=0; i < results[selectedRound].primary.length; i++) {
            var cell_ = document.getElementById("cell" + String(results[selectedRound].primary[i]));
            if (cell_) {
                cell_.style.backgroundColor=document.getElementsByTagName('body')[0].style.backgroundColor;
                cell_.style.color=document.getElementsByTagName('body')[0].style.color;
            }
        }
        for (var i=0; i < results[selectedRound].adds.length; i++) {
            var cell_ = document.getElementById("cell" + String(results[selectedRound].adds[i]));
            if (cell_) {
                cell_.style.backgroundColor=document.getElementsByTagName('body')[0].style.backgroundColor;
                cell_.style.color=document.getElementsByTagName('body')[0].style.color;
            }
        }

        console.log("painting starts");
        var tr_ = document.getElementById("orRow" + selectedRound);
        if (tr_) {
            if ("jackpot_won" in results[selectedRound] && results[selectedRound].jackpot_won === true) {
                tr_.style.backgroundColor = "#807d53";
            } else {
                tr_.style.backgroundColor = document.getElementsByTagName('body')[0].style.backgroundColor;
                tr_.style.color = document.getElementsByTagName('body')[0].style.color;
            }
        }
    } else {
        console.error("unacceptable round number: " + roundNumber);
    }

    for (var i=0; i < results[roundNumber].primary.length;i++) {
        var cell_ = document.getElementById("cell" + String(results[roundNumber].primary[i]));
        if (cell_) {
            if (cell_.selected == true) {
                cell_.style.backgroundColor="#386";
            } else {
                cell_.style.backgroundColor="#111";
            }
//            cell_.style.color="#000";
        }
    }
    for (var i=0; i < results[roundNumber].adds.length;i++) {
        var cell_ = document.getElementById("cell" + String(results[roundNumber].adds[i]));
        if (cell_) {
            if (cell_.selected == true) {
                cell_.style.backgroundColor="#866";
            } else {
                cell_.style.backgroundColor="#822";
            }
//            cell_.style.color="#000";
        }
    }
    tr_ = document.getElementById("orRow" + roundNumber);
    if (tr_) {
        tr_.style.backgroundColor = "#fff";
    }
    selectedRound = roundNumber;
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
        table_.innerHTML = "";
        var rows_ = Array();
        for (var i=0; i<2; i++) {
            rows_[i] = table_.insertRow(i);
        }
        var cell_;
        for (var i=0; i<games[game].numbersLimit; i++) {
            cell_ = rows_[0].insertCell(i);
            cell_.className += "tableCell";
            cell_.innerHTML=String(d1[i][1]);

            cell_ = rows_[1].insertCell(i);
            cell_.className += "tableCell";
            cell_.innerHTML=String(d2[i][1]);
        }
    }
    var tableLegend_ = document.getElementById("_oldResultsLegendTable_");
    tableLegend_.onclick = selectNumber;
    if (tableLegend_) {
        tableLegend_.innerHTML = "";
        var row = tableLegend_.insertRow(0);
        var cell_;
        for (var i=0; i<games[game].numbersLimit; i++) {
            cell_ = row.insertCell(i);
            cell_.className += "tableCell";
            cell_.id = "oldResultsStatsCell" + String(i+1);
            cell_.innerHTML=String(i+1);
            cell_.selected = false;
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
        
function showFieldsChanged(element) {
    if (!element.checked) {
        showFields = 0;
    } else {
        showFields = 1;
    }
    renderFields();
}

function renderFields() {
    var div_ = document.getElementById("fieldsTable");
    var plus_ = document.getElementById("fieldsPlus");
    var minus_ = document.getElementById("fieldsMinus");
    if (!showFields) {
        div_.style.visibility = "hidden";
        div_.style.display = "none";
    } else {
        div_.style.visibility = "visible";
        div_.style.display = "block";
    }
}

function updateHistSize() {
    var tempHistLength = $("#histLengthInput").val();
    console.log("checking new history size value:" + tempHistLength);
    if (tempHistLength >= results.length) {
        console.log("entered history value is too high");
        $("#histLengthInput").val(results.length);
        tempHistLength = results.length;
    }
    if (tempHistLength < 0) {
        console.log("entered history value is less than zero");
        $("#histLengthInput").val(30);
        tempHistLength = 30;
    }
    histLength = tempHistLength;
    setCookie("histLength", histLength, 365);
    drawHistory();
}

function processResults() {
    roundsCounter = results.length - 1;
    for (var i=0; i <= roundsCounter; i++) {
        // add main appearances
        for (var j=0; j < results[i].primary.length; j++) {
            var main = results[i].primary[j];
            d1[main-1][1] = d1[main-1][1] + 1;
        }
        for (var j=0; j < results[i].adds.length; j++) {
            var addit = results[i].adds[j];
            d2[addit-1][1] = d2[addit-1][1] + 1;
        }
        d6.push(d1.slice(0));
    }
    selectedRound = roundsCounter;
    drawHistory();
    setMinAvgMax();
    addFields();
    populateOldResultsStats();
    rerender(selectedRound);
}

function loadExtendedResultInfo(pgame, pyear, pweek_number, id) {
    var xmlhttp;
    if (window.XMLHttpRequest) {
        xmlhttp=new XMLHttpRequest();
    } else {
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange=function() {
        if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            var parsedResults = JSON.parse(xmlhttp.responseText);
            if (parsedResults== undefined) {
                console.log("Could not parse results data received from server");
                return;
            }
            for (var ridx=0; ridx <= parsedResults.length; ridx++) {
                console.log("checking if result " + parsedResults[ridx].id + " is suitable")
                if (parsedResults[ridx].id == id) {
                    processExtendedResultInfo(parsedResults[ridx]);
                    break;
                }
            }
        }
    }

    xmlhttp.open("GET","results/" + pgame + "_" + pyear + "_" + pweek_number + ".json", true);
    xmlhttp.send();
}

function processExtendedResultInfo(draw) {
    console.log("processing extended result " + draw.id);
    var drawDateDiv = document.getElementById("drawDate");
    if (drawDateDiv) {
        var drawtime = new Date(parseInt(draw["drawTime"]));
        drawDateDiv.innerHTML = ("" + drawtime).replace(/ GMT\+0.*/, '');
    }

    /* render table with payable prizes */
    var prizes = document.getElementById("prizesTable");
    if (!prizes) {
        console.log("ERROR: could not find prizesTable, will create");
        document.createElement("table");
    } else {
        prizes.innerHTML = "";
    }
    var header = prizes.insertRow(0);
    var headerCell = header.insertCell(0);
    headerCell.style.textAlign="center";
    headerCell.innerHTML = "Lucky ones";

    headerCell = header.insertCell(1);
    headerCell.style.textAlign="center";
    headerCell.innerHTML = "Prize";

    headerCell = header.insertCell(2);
    headerCell.style.textAlign="center";
    headerCell.innerHTML = "Combination";

    for (var i=0; i<draw["prizeTiers"].length; i++) {
        var prize = draw["prizeTiers"][i];
        var prizeRow = prizes.insertRow(1 + i);
        var prizeCell = prizeRow.insertCell(0);
        prizeCell.innerHTML = prize["shareCount"];
        if (i%2 == 1) {
            prizeRow.style.backgroundColor = "#444";
        }
        prizeCell = prizeRow.insertCell(1);
        var splitMe = String(prize["shareAmount"]);
        if (splitMe.length > 2) {
            splitMe = [splitMe.slice(0,splitMe.length-2),".",splitMe.slice(splitMe.length-2)].join("");
        }
        prizeCell.innerHTML =  "&nbsp" + splitMe  + "&nbsp";

        prizeCell = prizeRow.insertCell(2);
        prizeCell.innerHTML = "&nbsp&nbsp" + prize["name"];
    }
}

function rerender(newRound) {
    fieldsShowRound(newRound);
    swapImage(newRound);
    if (showExtendedResultInfo) {
       loadExtendedResultInfo(game, results[newRound].year, results[newRound].week, results[newRound].id);
    }
}

function prevResultShow() {
    if (selectedRound > (roundsCounter - histLength)) {
        rerender(selectedRound-1);
    }
}

function nextResultShow() {
    if (selectedRound <= (roundsCounter - 1)) {
        rerender(selectedRound + 1);
    }
}

