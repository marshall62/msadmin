// function test (msg) {
//     alert(msg);
// }
//
//
//
// // Given a props object , build a select element containing options that can be stuck inside the elt.
// // The options need to be like [{label: 'Has Audio', value:'hasAudio'}, {},...]
// function injectPulldownIntoElement (props, elt) {
//     var div = document.createElement('div');
//     div.className = 'input-group';
//     var inner = '<span class="input-group-addon">' +props.label+ '</span>';
//     // var s = {width: 'auto'};
//     var disable = props.isDisabled ? "disabled" : ""
//     inner += '<select id="' +props.myId+ '" name="' +props.myName+ '" class="form-control" ' +disable+ ' >';
//     for (var opt of props.options) {
//         var ovalu = opt.value;
//         if (props.selectedOption == ovalu)
//             inner += ('<option selected value="' +opt.value+ '">' + opt.label + '</option>');
//         else
//             inner += ('<option value="' +opt.value+ '">' + opt.label + '</option>');
//     }
//     inner += "</select>";
//     div.innerHTML = inner;
//
//     elt.appendChild(div);
//     // must set style of select after html is added to the div
//     // document.getElementById(props.myId).style.width = 'auto';
// }
//
//
// function getPulldownProps (eltId, options) {
//     var obj = {id: eltId};
//     obj.options = options;
//     obj.selectId = document.getElementById(eltId).getAttribute("selectId");
//     obj.label = document.getElementById(eltId).getAttribute("label");
//     obj.name = document.getElementById(eltId).getAttribute("name");
//     obj.selectedOption = document.getElementById(eltId).getAttribute("selectedOption");
//     return obj;
// }
//
// function clearPulldown (mountingEltId) {
//     var elt = document.getElementById(mountingEltId);
//     // remove anything that might be inside the div from previous mountings
//     while (elt.firstChild) {
//         elt.removeChild(elt.firstChild);
//     }
// }
//
//
//
// function mountPulldownComponent (mountingEltId, props) {
//     var propsInTag = getPulldownProps(mountingEltId,props)
//     var elt = document.getElementById(mountingEltId);
//     clearPulldown(mountingEltId);
//     if (elt) {
//         injectPulldownIntoElement(props, document.getElementById(mountingEltId));
//
//     }
//
// }





class ImageControls {
    // ImageControls needs to initialized with an imageURL (possibly null) or filename + imageId (possibly null), and
    // the URI that gets to the location of the filename if one is given (this is the place within our apache doc root)
    constructor(imageURL, filename, imageId, localImageURI) {

        if (filename) {
            this.imageId = imageId;
            this.filename = filename;
            this.mediaURI = localImageURI;
            this.imageURL = null;
        }
        else if (imageURL) {

            this.imageId = null;
            this.filename = null;
            this.imageURL = imageURL;
            this.mediaURI = null;
        }
        this.aRemoveImage = this.aFilename = this.imgPreview = null;
    }


    fileURL () {
        return this.mediaURI + this.filename;
    }

    removeImage () {
        $(this.previewDiv).remove();
        $(this.inputImageURL).val('');

    }


//
//  <div class="form-inline">
// <div class="input-group">
// <span class="input-group-addon">Image URL</span>
// {% if probId == -1 %}
// <input id="imageURL" type="text" class="form-control" name="imageURL" placeholder="">
// {% else %}
// <input id="imageURL" type="text" class="form-control" name="imageURL" value = "{{ problem.imageURL }}">
// {% endif %}
//
// </div>
// <input class="form-control mb-2 mr-sm-2 mb-sm-0" name="imageFile" type="file">
// <a href="#"><span class="glyphicon glyphicon-question-sign" data-toggle="tooltip" data-original-title="Either a URL to an image or else the name of the file you upload which can be referenced as {[myfile.jpg]}"></span></a>
// {% if problem.imageURL %}
// <div id="problemImagePreview">
// The Problem is currently using this figure from a URL:<br>
// <img id="imgpreview" onmouseover="this.removeAttribute('width'); this.removeAttribute('height');" onmouseout="this.width='50'; this.height='50';" width="50" height="50" src="{{ problem.getImageURL }}">
// <br><a id="imageFilename">{{ problem.getImageURL }}</a>
// <a class="delImage" href="#">
// <span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="Remove this image from the problem"></span>
// </a>
// </div>
// {% elif problem.imageFile %}
// <div id="problemImagePreview">
// The Problem is currently using this figure from a file:<br>
// <img id="imgpreview" onmouseover="this.removeAttribute('width'); this.removeAttribute('height');" onmouseout="this.width='50'; this.height='50';" width="50" height="50" src="{{ MEDIA_URL }}{{ problem.getProblemDir }}{{ problem.imageFile.filename }}">
// <br><a id="imageFilename">{{ MEDIA_URL }}{{ problem.getProblemDir }}{{ problem.imageFile.filename }}</a>
// <a class="delImage" href="#">
// <span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="Remove this image from the problem"></span>
// </a>
// </div>
// {% endif %}
// </div>


    // mainDiv = <div id=eltId class="form-inline">
    // The main div with id eltId is loaded with the HTML tags that define the image control correctly depending on how it was initialized in the constructor.
    // props allows passing in things that are specific to this instance of the component.  It is an object like {imageFileName: 'X', ...}.  They are:
    //    imageFileName: the name field of the <input type="file" name='X'
    //    delImageClassName:  the class name to set the adeleteImageTag to (needs to be different for problem and hints)
    // Will set the three instance variables: this.inputImageURL this.aRemoveImage this.aFilename this.imgPreview this.previewDiv which will be used in subsequent method calls
    // during the lifetime of this object.
    mountComponent (eltId, props) {
        var msgText = null,inputImageURLTag = null,afilenameTag=null;
        var imgPreviewTag=null,spanDeleteImageIconTag=null, adeleteImageTag=null;
        var mainDiv = $('#'+eltId);
        var inputImageURLTag = '<input id="imageURL" type="text" class="form-control" name="imageURL" placeholder="">';
        // An existing problem will need these controls.
        if (this.imageURL || this.imageId) {
            imgPreviewTag = '<img class="img_preview" onmouseover="this.removeAttribute(';
            imgPreviewTag += "'width'); this.removeAttribute('height');";
            imgPreviewTag += '" onmouseout="this.width=';
            imgPreviewTag += "'50'; this.height='50';";
            // note last bit of imgPreviewTag is appended below dependingon if its a file or a URL
            adeleteImageTag = this.getRemoveImageControls(props.delImageClassName);
            // span goes inside <a>
            // spanDeleteImageIconTag = '<span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="Remove this image from the problem"></span>';
            // adeleteImageTag = '<a class="a_delete_img" href="#">' + spanDeleteImageIconTag + "</a>";

        }
        // a problem with an image URL will need these
        if (this.imageURL) {
            imgPreviewTag += '" width="50" height="50" src="' + this.imageURL + '"> <br>';
            inputImageURLTag = '<input type="text" class="form-control" name="imageURL" value ="' + this.imageURL + '">';
            msgText = "The Problem is currently using this figure from a URL:<br>";
            afilenameTag = '<a class="a_img_filename">' + this.imageURL + '</a>';
        }
        // a problem with an image file will need these
        else if (this.imageId) {
            // this.fileURL return a full URL to the file as stored in our apache doc root
            imgPreviewTag += '" width="50" height="50" src="' + this.fileURL() + '"> <br>';
            msgText = "The Problem is currently using this figure from a file:<br>";
            afilenameTag = '<a class="a_img_filename">' + this.fileURL() + '</a>';
        }
        // Add elements to the main div that are always present
        var inpDiv = $('<div class="input-group"></div>').appendTo(mainDiv);
        // note:  We don't need to hold any of these elements in instance variables.
        var span = '<span class="input-group-addon">Image URL</span>';
        var fileInputTag = '<input class="form-control mb-2 mr-sm-2 mb-sm-0" name="' +props.imageFileName+ '" type="file">';
        var helpIcon = '<a href="#"><span class="glyphicon glyphicon-question-sign" data-toggle="tooltip" data-original-title="Either a URL to an image or else you may upload an image file"></span></a>';
        inpDiv.append(span); // a label saying "Image URL"
        this.inputImageURL = $(inputImageURLTag).appendTo(inpDiv);
        this.inputFile = $(fileInputTag).appendTo(mainDiv);
        mainDiv.append(helpIcon); // an <a> tag that provides help if you hover over the icon in the span.
        // Now, if there is an imageURL or an imageFile add a second div that contains preview elements

        // If there is an image URL or an image File, put in the preview controls.
        if (this.imageURL || this.imageId) {
            this.previewDiv = $('<div class="imgPreviewDiv"></div>').appendTo(mainDiv);
            this.previewDiv.append(msgText);
            this.imgPreview = $(imgPreviewTag).appendTo(this.previewDiv);
            this.previewDiv.append('<br>');
            this.aFilename = $(afilenameTag).appendTo(this.previewDiv);
            this.aRemoveImage = $(adeleteImageTag).appendTo(this.previewDiv);
        }
    }


    getRemoveImageControls (className) {
        // span goes inside <a>
        var spanDeleteImageIconTag = '<span class="glyphicon glyphicon-remove" data-toggle="tooltip" data-original-title="Remove this image"></span>';
        var adeleteImageTag = '<a class="' +className+ '" href="#">' + spanDeleteImageIconTag + "</a>";
        return adeleteImageTag;
    }

    removeImagePreview () {
        this.inputImageURL.val('');
        this.previewDiv.empty();
        this.previewDiv.hide();
    }

    setImage (imageURL, filename, fileId) {
        if (this.aRemoveImage)
            this.aRemoveImage.remove();
        if (imageURL) {
            this.imgPreview.attr('src',imageURL);
            this.inputImageURL.val(imageURL);
            this.aFilename.text(imageURL);
            this.inputFile.val('');
            adeleteImageTag = this.getRemoveImageControls ();
            this.aRemoveImage = $(adeleteImageTag).appendTo(this.previewDiv);
            this.previewDiv.show();

        }
        else if (filename) {
            this.imgPreview.attr('src',this.mediaURI+"/"+filename);
            this.inputImageURL.val('');
            this.aFilename.text(data.imageFilename);
            this.inputFile.val('');
            adeleteImageTag = imageRemoveControls ();
            this.aRemoveImage = $(adeleteImageTag).appendTo(this.previewDiv);
            this.previewDiv.show();
        }
        else {
            this.previewDiv.hide();
            this.inputImageURL.val('');
            this.aFilename.text('');
            this.inputFile.val('');
        }
    }


}





