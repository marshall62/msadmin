// Called when the user clicks the save button on problem creation or edit.
// Will show warnings for incomplete fields to the user and give options to continue or cancel.
function checkSnapshotValidity () {
    $('#warningDialog').modal('show');
}

$('#saveButton').on('click', function() {
    var status = $('#my-pulldown3').val();
    var warningString = "";
    if (status === 'ready' && $(this).data('snapshot') == 0) {
        if ($(this).data('snapshot') == 0) {
            warningString += "snapshot";
        }
        if ($(this).data('hint') == "True") {
            if (warningString.length) {
                warningString += " or hint";
            }
            else {
                warningString += "hint";
            }
        }
        if ($(this).data('video') == 0) {
            if (warningString.length) {
                warningString += " or video";
            }
            else {
                warningString += "video";
            }
        }
        if ($(this).data('example') == 0) {
            if (warningString.length) {
                warningString += " or example";
            }
            else {
                warningString += "example";
            }
        }
        $('#warning-text').text("You are saving the question without any " + warningString + ". Are you sure you want to continue?");
        $('#warningDialog').modal('show');
    }
    else {
        $('#editProblem').submit();
    }
});