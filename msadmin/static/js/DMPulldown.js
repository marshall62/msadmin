/**
 * Created by marshall on 4/16/18.
 */


/**
  Allows extending the jquery selector with DMPulldown method
  $('#myPulldown').DMPulldown({
     options: [{"label": "New York", "value": "ny"}, {"label": "Vermont", "value": "vt"}],
     selectedOption: 'ny',
     onChange: function () { testChg();}
  })
 *
 */

// TODO should probably require a 'dmpulldown' class to be on the select element and if its not there, this would do nothing
jQuery.fn.extend({
    DMPulldown: function() {
        var obj= arguments[0];
        var options = obj.options;
        var selectedOption = obj.selectedOption;
        var chgFn = obj.onChange;
        // get rid of any <option> elements that may be there already.
        $(this).empty();
        $(this).change(chgFn);

        for (var opt of options) {
            var ovalu = opt.value;
            if (selectedOption == ovalu)
                $(this).append('<option selected value="' +opt.value+ '">' + opt.label + '</option>');
            else
                $(this).append('<option value="' +opt.value+ '">' + opt.label + '</option>');
        }
    }
});


jQuery.fn.extend({
    setDMPulldownOptions: function () {
        var obj = arguments[0];
        var options = obj.options;
        var selectedOption = obj.selectedOption;
        if (options) {
            $(this).empty();
            for (var opt of options) {
                var ovalu = opt.value;
                if (selectedOption == ovalu)
                    $(this).append('<option selected value="' + opt.value + '">' + opt.label + '</option>');
                else
                    $(this).append('<option value="' + opt.value + '">' + opt.label + '</option>');
            }
        }
    }
});

/*

// Test The above.

function testChg () {
    console.log("testChg");
}


$(document).ready(function() {
    $('#myPulldown').DMPulldown({
        options: [{"label": "New York", "value": "ny"}, {"label": "Vermont", "value": "vt"}],
        selectedOption: 'ny',
        onChange: testChg
    });
}

*/