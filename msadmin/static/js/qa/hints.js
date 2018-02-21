/**
 * Created by marshall on 12/5/17.
 */
////  Functions that support Hints


function validateHint () {
    return true;
}

function loadHintDialogAudio (theHint, hintPath) {
    if (theHint.audioResource) {
        // $('#haudioResource').val(theHint.audioResource);
        $('#haudioFilename').text(theHint.audioResource);
        $('#hintAudioMP3').attr('src',hintPath  +theHint.audioResource );
        $('#haudioFile').val('');
        $('#hintAudio').show();
        var audio = $('#haudioPlayer');
        audio[0].load();
    }
    else {
        $('#hintAudio').hide();
        // $('#haudioResource').val('');
        $('#haudioFile').val('');
    }
}

function loadHintDialogImage (theHint, hintPath) {
    if (hintImageControls)
        $('#hintImageControls').empty();
    // problemDir is a global set in quath_edit.html
    hintImageControls = new ImageControls(theHint.imageURL,theHint.imageFilename,theHint.imageFileId,hintPath);
    hintImageControls.mountComponent('hintImageControls',{imageFileName: 'imageFile',delImageClassName: 'a_hint_delete_img'});

}

function addHintMediaFiles (mfs) {
    $('#hmediatbody').empty();
    for (mf of mfs) {
        addHintMediaFile(mf);
        // $('#hmediatbody').append("<tr><td><input type='checkbox'></td><td>" +mf.id+ "</td><td>{[" +mf.filename+ "]}</td><td></td></tr>")
    }
}

function addHintMediaFile (data=null) {
    var tddel = sprintf("<td><input name='deletehMediaFile[]' value='%s' type='checkbox'></td>",data?data.id:'');
    var tdid = data ? "<td>" + data.id+ "</td>" : "<td></td>";
    var tdfname = data ? "<td>{[" + data.filename + "]}</td>" : "<td></td>";
    var tdupload = data ? "<td></td>" : '<td><input name="hmediaFiles[]" type="file"></td></td>';
    var tr = ( data ? "<tr id='" + data.id + "'>" : "<tr>" ) + tddel + tdid + tdfname + tdupload + "</tr>";
    $('#hmediaTable > tbody:last-child').append(tr);

}

function loadHintDialogData(id, theHint, problemPath) {
    var hintPath= problemPath+"hint_"+theHint.id + "/";
    $('#hid').val(id);
    $('#hname').val(theHint.name);
    // $('#haudioResource').val(theHint.audioResource);
    // Adds the audioResource (filename) to the <a> tag contents which includes a clickable delete icon
    // $('#removeHintAudio').append(theHint.audioResource);
    $('#hstatement').val(theHint.statementHTML);
    $('#order').val(theHint.order);
    $('#hoverText').val(theHint.hoverText);
    $('#givesAnswer').prop('checked',theHint.givesAnswer);
    loadHintDialogAudio(theHint,hintPath);
    loadHintDialogImage(theHint, hintPath);
    // add rows to hint's media files table
    addHintMediaFiles(theHint.mediaFiles);
    // console.log("mounting " );
    mountImagePlacementPulldown(theHint.placement);
    setHintErrorMessage('');
    $('#hintSaveMessage').html('');
    // close all accordions before opening
    $('.collapse').collapse('hide')
}



// Called when the user clicks the edit icon of a hint.
// Will get the hint JSON from the server and will pop up the dialog to edit it.
function editHint2 (id, problemPath) {
    hintEditMode = EXISTING_HINT;
    var url_mask = GET_HINT_URL.replace(/12345/, id.toString());
    $.get(url_mask, function(data) {
        theHint= data;
        loadHintDialogData(id, theHint, problemPath);
        showHintDialog();

    });
}

// WHen the user clicks the save and continue button within the hint dialog,
// we call the server to get the latest hint JSON, and then refresh the fields
// that may be stale: audio, image, and media files.
function refreshHintDialog (id, problemPath) {
    var url_mask = GET_HINT_URL.replace(/12345/, id.toString());
    $.get(url_mask, function(data) {
        theHint= data;
        $('#hid').val(theHint.id); // new hints need to have their ID put in
        var hintPath= problemPath+"hint_"+theHint.id + "/";
        loadHintDialogAudio(theHint,hintPath);
        loadHintDialogImage(theHint,hintPath);
        // add rows to hint's media files table
        addHintMediaFiles(theHint.mediaFiles);

    });
}

function mountImagePlacementPulldown (placement) {
    var opts = [{label: 'Replace problem figure', value:'1'},{label: 'Inside hint figure', value:'2'}];
    mountPulldownComponent('my-pulldown5',{label:"Image placement", myId:"imageplacement", myName:"himage_placement", selectedOption:placement, options: opts});

}

// Called when the user clicks the + hint button to add a new hint.
// Clears the dialog fields and pops it up.
function addHint () {
    hintEditMode = NEW_HINT;
    var numHints = theProblem.numHints + 1;
    theHint = {order: theProblem.numHints, name: 'Hint ' + numHints};
    $('#hid').val('');
    $('#hname').val('Hint ' + numHints);
    // $('#haudioResource').val('');
    $('#haudioFile').val('');
    $('#hintAudioMP3').attr('src','' );
    $('#hintAudio').hide();
    $('#hstatement').val('');
    $('#order').val('');
    $('#hoverText').val('');
    $('#givesAnswer').prop('checked',false);
    $('#himageURL').val('');
    $('#himageFile').val('');
    $('#himageFilename').text(''); // an <a> tag that has the filename
    $('#himage').attr('src','');
    $('#himageDiv').hide();
    $('#hmediatbody').empty();
    if (hintImageControls)
        $('#hintImageControls').empty();
    hintImageControls = new ImageControls(null,null,null,null);
    hintImageControls.mountComponent('hintImageControls',{imageFileName: 'imageFile',delImageClassName: 'a_hint_delete_img'});

    mountImagePlacementPulldown('2');
    showHintDialog();
    setHintErrorMessage('');
    // close all accordions before opening
    $('.collapse').collapse('hide')

}


//  If an existing row is edited with the hint dialog, this is called after the save AJAX returns the
// updated info about the hint.   The statement html is updated.
function updateHintRow (hint) {

    rowN = hint.order
    console.log('updating row ' + rowN);
    // the givesAnswer, hovertext, statementHTML, name can change.  Only name, statementHTML is in table row
    var rows = $('tr', $('#hinttbody'));
    var r = rows.eq(rowN);
    var td = r.find('.statement'); // td containing HTML of statement
    td.html(hint.statementHTML);
    // set the check mark about giving answer appropriately
    td = r.find('.givesAnswer');
    // if the hints gives the answer we want a check in the row; else remove if there is one
    if (hint.givesAnswer) {
        console.log('adding check');
        $('span',td).remove();
        td.append('<span class="glyphicon glyphicon-ok"></span>');
    }
    else {
        console.log('removing check');
        $('span',td).remove();
    }
    removeHintAlert(rowN); // eliminate any alerts in the row.  validation of hints will happen afer this runs.

}

function getHintRowNumber (hintId) {

    // the givesAnswer, hovertext, statementHTML, name can change.  Only name, statementHTML is in table row
    var rows = $('tr', $('#hinttbody'));
    var foundAt=-1;
    rows.each(function (i) {
        if ($('td:contains('+hintId+')', $(this)).length > 0) {
            foundAt=i;
            return false; // exits the iteration
        }
    });
    return foundAt;
}


// When the hint dialog is saved an ajax call gets back the new hints JSON and then calls this function
// to add a new row to the hint table.
function addHintRow2 (hint) {
    // problemDir is a global defined in qauth_edit.html - it points to the directory for the problem
    var editIcon = '<a href="#hinttbody" class="hint-edit-icon" onClick="editHint2(' +hint.id+ ', problemDir)"><span class="glyphicon glyphicon-pencil" data-toggle="tooltip" data-original-title="Edit this hint"></span></a>';
    var tr = '<tr id="' +hint.id+ '" class="dnd"><td><input type="checkbox"></td>' +
        '<td class="edit-hint">' +editIcon + '</td>' +
        '<td class="hint-id">' + hint.id + '</td>' +
        '<td class="givesAnswer">' + (hint.givesAnswer ? '<span class="glyphicon glyphicon-ok"></span>' : '') + '</td>' +
        '<td class="statement"> ' + hint.statementHTML + '</td></tr>';
    $('#hinttbody').append(tr);
}



// When dialog save button is clicked, save the hint.
// Closes the dialog if isExit is true.
// Closes after POST has been sent to the server but before results return
// Shows an hourglass icon, and does not close the dialog until results
// are returned from the server.
function saveHint (isExit) {
    var form = $('#hintForm')[0]; // get the Javascript obj for the hint form
    var data = new FormData(form); // put all the form fields into data
    var probId = theProblem.id;
    // get the row # of this hint
    var rown = getHintRowNumber(theHint.id);
    data.append('order',rown);
    setWaitCursor(true); // change cursor to hourglass while waiting for save.
    var url_mask = SAVE_HINT_URL.replace(/12345/, probId.toString());
    // note processData and contentType are both false to correctly send post with files.
    $.ajax({
        url: url_mask,
        type: "POST",
        data: data,
        processData: false,
        contentType: false,
        error: function (a,b,c) {
            console.log("Failed to write to server! " + a.responseText + b);
            console.log(a);
            alert("Failed to write to server! " + a.responseText + b);
            setWaitCursor(false);
        },
        success: function (data) {
            // Expects {'hint': hintJSON, success: 0|1, 'message': text}
            // Whenever either save button is clicked we make modifications to the Hints table
            // display in the problem (either add a row or update an existing row).
            // If the dialog is being exited, we validate hints and take the dialog down.
            // If the dialog is continued, we refresh its fields with new hint data from the server.
            theHint = data.hint;
            var message = data.message;
            var savemessage = data.saveMessage;
            var succeeded = data.success==1; // errors deleting media files => 0
            if (hintEditMode == NEW_HINT) {
                theProblem.numHints++;
                addHintRow2(theHint);
                hintEditMode = EXISTING_HINT;
            }
            else {
                updateHintRow(theHint);
            }
            if (isExit && succeeded) {
                validateHints();
                $('#hintDialog').modal('toggle');
            }
            else {
                refreshHintDialog(theHint.id, problemDir);
                setHintErrorMessage(message);
            }
            $('#hintSaveMessage').html(savemessage);
            setWaitCursor(false);

        }
    });
}

// every time a drag and drop of a hint row is completed we update the server with the full list of hints in the
// order that they now are.   .
function saveHintsToServer () {
    var rows = $('tr', $('#hinttbody'));
    var ids = [];
    rows.each(function () {
        // get the ID out of the td
        var id = $('.hint-id', $(this)).html();
        ids.push(id);
    });
    var data = {hintIds: ids}
    // post hint sequence to the server
    var url_mask = SAVE_HINTS_URL.replace(/12345/, theProblem.id.toString());
    // note processData and contentType are both false to correctly send post with files.
    $.ajax({
        url: url_mask,
        type: "POST",
        data: data,
        error: function (a,b,c) {
            console.log("Failed to write to server! " + a.responseText + b);
            console.log(a);
            alert("Failed to write to server! " + a.responseText + b);
        },
        success: function (data) {
        }
    });
}

// Puts a message below the hint table so user knows there is an error in the hints.
function setHintErrorMessage (msg) {
    if (msg) {
        $('#hmediaFileErrorMessages').html(msg);
    }
    else
        $('#hmediaFileErrorMessages').html('');
}


// add an alert symbol next to the hint ID in row N
// resulting td will be like:
// <td class="edit-hint"><a><span class="glyphicon-alert"></span></a> <span style="padding-left"> <a class="hint-edit-icon"><span glyphicon-pencil</a>
function setHintAlert (rowN, msg) {
    console.log("setting hint alert at row " + rowN + msg );
    var rows = $('tr', $('#hinttbody'));
    var r = rows.eq(rowN);
    var td = r.find('.edit-hint'); // td containing with class "edit-hint
    var xalert = $('.glyphicon-alert',td).length;
    // see if there is already an alert there
    if (xalert > 0)
        return;
    var iconATag = td.find('a'); // the <a> tag within td
    var alertIcon = '<a href="#hinttbody"><span style="color: red" class="glyphicon glyphicon-alert" data-toggle="tooltip" data-original-title="'+msg+'"></span></a>';

    td.html(alertIcon + '<span style="padding-left:10px">');
    td.append(iconATag);
    $('[data-toggle="tooltip"]',td).tooltip({
        placement : 'top'
    });

}



// remove the alert icon and spacing from the td of the hint edit-icon
function removeHintAlert (rowN) {
    var rows = $('tr', $('#hinttbody'));
    var r = rows.eq(rowN);
    var td = r.find('.edit-hint'); // get the edit-hint td
    // eliminate all children that are not the edit icon
    td.children().each(function (x) {
        if (!$(this).hasClass('hint-edit-icon'))
            $(this).remove();
    });

}

// The drag and drop of hint rows allows for invalid things like:
// a show-answer hint not at the end
// If a situation like this is found, put an alert symbol next to the offending hint.
// Must return true/false if valid/not valid
function validateHints () {
    var numRows = $('#hinttbody tr').length;
    var answerError = false;
    if (numRows > 0) {
        var rows = $('tr', $('#hinttbody'));
        var i = 0, foundAt = -1;

        // find the <a class="hint-edit-icon  that contains the hints name
        rows.each(function () {
            // remove any alert in this row first
            removeHintAlert(i);
            // get the <td class="givesAnswer" and see if it contains an <span> tag which is an indication that it has the
            // check icon indicating that this hint gives the answer.
            var tdga = $(this).find(".givesAnswer > span");
            if (tdga.length > 0)
                if (i != numRows-1) {
                    setHintAlert(i, "The hint that gives the answer must be the last one in the sequence.");
                    answerError = true;
                }
            i++;
        });
        if (answerError) {
            setHintErrorMessage('Only the last hint can give the answer.');
            return false;
        }
        // if valid remove any alert that might be in the last (Show Answer row)
        removeHintAlert(numRows-1);
        setHintErrorMessage(null);
        return true;

    }
    else return true;
}

// go through each hint row and set its name to "Hint i" .  Do not change name of
// hint with name "Show Answer"
function relabelHints () {
    var n=1;
    $('#hinttbody').find('tr').each(function () {
        var row = $(this);

        var name = row.find('.hint-edit-icon')
        if (name.html() != 'Show Answer') {
            name.html('Hint ' + n);
            n++;
        }

    });
}

// Delete all the selected hints
function deleteSelectedHints (probId) {
    if (confirm("Are you sure you want to delete the selected hints?")) {
        var ids = [];

        $('#hintTable').find('tr').each(function () {
            var row = $(this);
            if (row.find('input[type="checkbox"]').is(':checked') ) {
                var rid = row.attr('id');
                ids.push(rid);
                theProblem.numHints--;
                row.remove();

            }
        });


        var url_mask = DELETE_HINTS_URL.replace(/12345/, probId.toString());
        $.ajax({
            url: url_mask,
            type: "POST",
            data: {data: ids },
            error: function (a,b,c) {
                console.log("Failed to delete hints! " + a.responseText + b);
                console.log(a);
                alert("Failed to delete hints " + a.responseText + b);
            },
            success: function (data) {
               validateHints();
            }
        });
    }
}

function removeHintImage (hintImageControls) {
    if (confirm("Do you want to delete the hint image")) {
        var url_mask = REMOVE_HINT_IMAGE_URL.replace('12345',theHint.id);
        $.ajax({
            url: url_mask,
            type: "DELETE",
            error: function (a,b,c) {
                alert("Failed to get problem " + a.responseText + b);
            },
            success: function (data) {
                console.log("successful delete of hint image");
                hintImageControls.removeImagePreview();
            }
        });
    }
}



// opens the hint dialog
function showHintDialog () {
    $('#hintDialog').modal('show');
}

////////  End of Functions that operate on Hints //////////////
