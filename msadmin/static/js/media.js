/**
 * Created by marshall on 12/5/17.
 */
//////////////  Functions that work on media table /////////////////

// Called when the save button under the media files is clicked.  There can be checked rows to delete some media files
// and there can be newly added rows.   We confirm that the user wants to do the deletes and then send both the upload files and
// the deleteIds to the server to process.  We get back the list of media files from the server, empty the table, and reload it with the
// returned data.
function saveMediaFiles () {
    if ($('#mediatbody input[type="checkbox"]:checked').length > 0 &&
        !confirm("Are you sure you want to delete the selected media files?")) {
        return;
    }
    var deleteIds = processSelectedMediaFileIds();

    // The form contains multi-part data for multiple file uploads in each table row.
    var form = $('#mediaFilesForm')[0]; // get the Javascript obj for the media file form
    var data = new FormData(form); // put all the form fields into data
    var probId = theProblem.id;
    if (deleteIds.length > 0)
        for (i of deleteIds)
            data.append('deleteIds[]', i);
    var url_mask = SAVE_MEDIA_URL.replace(/12345/, probId.toString());
    $.ajax({
        url: url_mask,
        type: "POST",
        data: data,
        processData: false,
        contentType: false,
        error: function (a, b, c) {
            console.log("Failed to process media! " + a.responseText + b);
            console.log(a);
            alert("Failed to process media " + a.responseText + b);
        },
        success: function (data) {
            $('#mediatbody').empty();
            for (f of data)
                addMediaRow(f);
        }
    });

}

function addMediaRow (data = null) {
    console.log("add media row");
    var tddel = "<td><input type='checkbox'></td>";
    var tdid = data ? "<td>" + data.id+ "</td>" : "<td></td>";
    var tdfname = data ? "<td>" + data.filename + "</td>" : "<td></td>";
    var tdupload = data ? "<td></td>" : '<td><input name="mediaFiles[]" type="file"></td></td>';
    var tr = ( data ? "<tr id='" + data.id + "'>" : "<tr>" ) + tddel + tdid + tdfname + tdupload + "</tr>";
    $('#mediaTable > tbody:last-child').append(tr);
}


// go through the rows that are selected for deletion and remove them.  Also return the list of ids.
function processSelectedMediaFileIds () {
    var deleteIds = [];
    $('#mediatbody').find('tr').each(function () {

        var row = $(this);
        if (row.find('input[type="checkbox"]').is(':checked')) {
            var rid = row.attr('id');
            if (rid)
                deleteIds.push(rid);
            row.remove();

        }
    });
    return deleteIds;

}


// function deleteSelectedMedia () {
//     if (confirm("Are you sure you want to delete the selected media files?")) {
//         var deleteIds = [];
//
//         var probId = theProblem.id;
//         $('#mediatbody').find('tr').each(function () {
//
//             var row = $(this);
//             if (row.find('input[type="checkbox"]').is(':checked') ) {
//                 var rid = row.attr('id');
//                 if (rid) {
//                     deleteIds.push(rid);
//                     row.remove();
//                 }
//
//             }
//         });
//
//         if (deleteIds.length > 0) {
//
//             var url_mask = "{% url 'qauth_delete_media' probId=12345 %}".replace(/12345/, probId.toString());
//             $.ajax({
//                 url: url_mask,
//                 type: "POST",
//                 data: {data: deleteIds },
//                 error: function (a,b,c) {
//                     console.log("Failed to delete media! " + a.responseText + b);
//                     console.log(a);
//                     alert("Failed to delete media " + a.responseText + b);
//                 },
//                 success: function (data) {
//                     // location.href = "{% url 'qauth_edit_prob' probId=12345 %}".replace(/12345/, probId.toString());
//                 }
//             });
//         }
//     }
// }






