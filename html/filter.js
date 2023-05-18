filterDiv=undefined;

function showFilter(filterDiv) {
    if (filterDiv == undefined)
        return;
    filter_block = filterDiv;

    var beforeCoutnerDiv = 

    for (var int i = 0; i < games[game].numbers; i++) {
        showFilterAddRow("numbers",filterDiv); /* uses "numbersStart" and "numbersLimit" */
    }
    for (var int i = 0; i < games[game].additionalNumbers; i++) {
        showFilterAddRow("additionalNumbers",filterDiv); /* uses "additionalNumbersStart" and "additionalNumbersLimit" */
    }
}

function showFilterAddRow(type, filterDiv) {
    var rangeIndex = document.createElement("div"); /* drawNumberIndex   */
    var newDiv     = document.createElement("div"); /* line              */
    var leftCond   = document.createElement("div"); /* left range cond   */
    var leftValue  = document.createElement("div"); /* left range end    */
    var rightValue = document.createElement("div"); /* right range end   */
    var rightCond  = document.createElement("div"); /* right range  cond */

    rangeIndex.style.display="inline-block";
    leftCond.style.display  ="inline-block";
    leftValue.style.display ="inline-block";
    rightCond.style.display ="inline-block";
    rightCond.style.display ="inline-block";

    rangeIndex.innerHtml = i;
    leftCond = "<=";
    rightCond = ">=";
    leftValue = games[game][type + "Start"];
    rightValue = games[game][type + "Limit"];


    newDiv.appendChild(leftValue);
    newDiv.appendChild(leftCond);
    newDiv.appendChild(rangeIndex);
    newDiv.appendChild(rightCond);
    newDiv.appendChild(rightValue);

    filterDiv.appendChild(newDiv);
}
