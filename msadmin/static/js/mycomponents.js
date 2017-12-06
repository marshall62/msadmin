function test (msg) {
    alert(msg);
}



// Given a props object , build a select element containing options that can be stuck inside the elt.
function injectPulldownIntoElement (props, elt) {
    var div = document.createElement('div');
    div.className = 'input-group';
    var inner = '<span class="input-group-addon">' +props.label+ '</span>';
    var s = {width: 'auto'};
    inner += '<select id="' +props.myId+ '" name="' +props.myName+ '" class="form-control" >';
    for (var opt of props.options) {
        var ovalu = opt.value;
        if (props.selectedOption == ovalu)
            inner += ('<option selected value="' +opt.value+ '">' + opt.label + '</option>');
        else
            inner += ('<option value="' +opt.value+ '">' + opt.label + '</option>');
    }
    inner += "</select>";
    div.innerHTML = inner;

    elt.appendChild(div);
    // must set style of select after html is added to the div
    document.getElementById(props.myId).style.width = 'auto';
}


function getPulldownProps (eltId, options) {
    var obj = {id: eltId};
    obj.options = options;
    obj.label = document.getElementById(eltId).getAttribute("label");
    obj.myName = document.getElementById(eltId).getAttribute("myName");
    obj.selectedOption = document.getElementById(eltId).getAttribute("selectedOption");
    return obj;
}

function mountPulldownComponent (mountingEltId, props) {
    var elt = document.getElementById(mountingEltId);
    // remove anything that might be inside the div from previous mountings
    console.log("Removing old content from " + mountingEltId);
    while (elt.firstChild) {
        elt.removeChild(elt.firstChild);
    }
    if (elt) {
        injectPulldownIntoElement(props, document.getElementById(mountingEltId));

    }

}





