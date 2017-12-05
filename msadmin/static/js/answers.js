/**
 * Created by marshall on 12/5/17.
 */
///////  Functions that operate on the answer table ////////////////////

function addMultiChoiceRows (n) {
    var numRows = $('#multichoicetablebody tr').length;
    if (numRows + n > choiceLabels.length) {
        alert("Cannot add more choices.");
        return;
    }
    for (var i = numChoices; i < numChoices+n; i++) {
        var tddel ='<td class="deleteButton">' +
            '<a class="delChoice" href="#multichoices">' +
            '<span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="Delete this choice"></span>'+
            '</a>'+
            '</td>';
        var tdlab = '<td class="choiceLabel">' + choiceLabels[i] + '</td>';
        var tdradio = '<td class="choiceCorrect"><input class="correctRadio" type="radio" name="correctChoice" value="' +choiceLabels[i]+ '"></td>';
        var tdtxt = '<td><div class="row"><div class="form-group col-lg-12">' +
            '<input name="multichoice[]" type="text" class="form-control" value=""/>' +
            "</div>" +
            "</div></td>";

        var tr="<tr>" + tddel + tdlab + tdradio + tdtxt + "</tr>";

        $('#multichoicetable > tbody:last-child').append(tr);
    }
    numChoices += n;
    showDebug();
}

function addShortAnswerRows (n) {
    // $("#multichoicetablebody").empty();

    for (var i = 0; i < n; i++) {
        var tddel ='<td class="deleteButton">'+
            '<a class="delShortAnswer" href="#shortanswertable">'+
            '<span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="Delete this answer"></span>'+
            '</a>'+
            '</td>';

        var tdtxt = '<td><div class="row"><div class="form-group col-lg-12">' +
            '<input type="text" class="form-control" name="shortanswer[]" value=""/>' +
            "</div>" +
            "</div></td>";

        var tr="<tr>" + tddel + tdtxt + "</tr>";

        $('#shortanswertable > tbody:last-child').append(tr);
        numAnswers++
    }
}

function getChildWithClass (element, classname) {
    for (c of element.children) {
        if (c.className === classname)
            return c;
    }
    return null;
}

function showDebug () {
    var tbody = document.getElementById("multichoicetablebody");
    console.log("-------------------");
    for (var i = 0, row; row = tbody.rows[i]; i++) {
        var c = row.cells[0];
        var cell = row.cells[2];

        console.log(cell);
        var inp = cell.childNodes[0];
        inp = getChildWithClass(cell,"correctRadio")
        inp.value = choiceLabels[i];
        console.log("Row " + i + " " + inp.name + ":" + "choiceval: " + inp.value + " checked: " + inp.checked );
        console.log(inp);
    }
    console.log("-------------------");

}

function labelChoices () {
    var tbody = document.getElementById("multichoicetablebody");
    for (var i = 0, row; row = tbody.rows[i]; i++) {
        //iterate through rows
        //rows would be accessed using the "row" variable assigned in the for loop
        for (var j=0, cell; cell=tbody.rows[i].cells[j]; j++)
            if (cell.className == "choiceLabel") {
                cell.innerHTML = choiceLabels[i];

            }
            // the radio button for marking correct choice needs to have its value changed to the new letter (same as label letter)
            else if (cell.className == "choiceCorrect")  {
                var inp = getChildWithClass(cell,"correctRadio");
                inp.value = choiceLabels[i];

            }



    }
    showDebug();
}

// GIven the 0-based row number in the multichoice table, delete that row
function deleteChoice (n) {
    var numRows = $('#multichoicetablebody tr').length;
    if (numRows == 2) {
        alert("A multi choice problem should have at least 2 choices.");
        return;
    }
    document.getElementById("multichoicetablebody").deleteRow(n);
    numChoices--;
    labelChoices();
}

// given the <a> element in the row that triggered the delete action
function deleteMultiChoiceRow (aTagDelButton) {
    var numRows = $('#multichoicetablebody tr').length;
    if (numRows == 2) {
        alert("A multi choice problem should have at least 2 choices.");
        return;
    }
    var td = aTagDelButton.parent();
    var tr = td.parent();
    var tbody = tr.parent();
    tr.remove();
    numChoices--;
    labelChoices()
}

function deleteAnswerRow (aTagDelButton) {
    var numRows = $('#shortanswertablebody tr').length;
    if (numRows == 1) {
        alert("A short answer problem should have at least 1 answer.");
        return;
    }
    var td = aTagDelButton.parent();
    var tr = td.parent();
    var tbody = tr.parent();
    numAnswers--
    tr.remove();
}

// no longer using checkboxes on rows to indicate deleting
// function deleteCheckedMultiChoiceRows () {
//     var numRows = $('#multichoicetablebody tr').length;
//
//     var numChecked = $('#multichoicetablebody tr td input[name="deleteChoice"]:checked').length;
//     if ((numRows-numChecked) < 2) {
//         alert("A multi choice problem should have at least 2 choices.");
//         return;
//     }
//     numChoices -= numChecked;
//     $('#multichoicetablebody tr').has('input[name="deleteChoice"]:checked').remove();
//     labelChoices();
// }



function exposeMultiChoiceControls () {
    $('#multichoices').show();
    $('#shortAnswer').hide();
}

function exposeShortAnswerControls () {
    $('#multichoices').hide();
    $('#shortAnswer').show();
}

function hasShortAnswer () {
    return $('#shortanswertablebody tr:first input').val() != ''
}
