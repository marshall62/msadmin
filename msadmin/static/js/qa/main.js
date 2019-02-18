// Called when the user clicks the save button on problem creation or edit.
// Will show warnings for incomplete fields to the user and give options to continue or cancel.
function checkSnapshotValidity () {
    $('#warningDialog').modal('show');
}

$('#saveButton').on('click', function() {
    var status = $('#my-pulldown3').val();
    if (status === 'ready' && $(this).data('snapshot') == 0) {
        $('#warningDialog').modal('show');
    }
    else {
        $('#editProblem').submit();
    }
});