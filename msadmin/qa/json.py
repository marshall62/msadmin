from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from msadminsite.settings import SNAPSHOT_DIRNAME
from .util import  write_file
import re

from msadmin.qa.qauth_model import Problem, ProblemMediaFile, Hint, ProblemLayout
from msadmin.qa.util import handle_uploaded_file, deleteMediaFile


def getProblemMediaRefs (problem, mediaFile):
    refs = findRefsInMain(problem.imageFile_id, problem.audioFile_id,mediaFile)
    if not refs:
        refs = findRefsInStatementHTML(problem.statementHTML, mediaFile.filename)
    return refs


# Return True if the media file is referenced using the {[filename]} syntax
def findRefsInStatementHTML (statementHTML, mediaFilename):
    res = re.search( r'\{\[\s*' +mediaFilename+ '\s*\]\}.*', statementHTML, re.M|re.I)
    return res

def findRefsInMain (imgFileId, audFileId, mf):
    return (imgFileId and imgFileId == int(mf.id)) or (audFileId and audFileId == int(mf.id))

# The media file failed to be deleted because it is referenced in the main or in the statement HTML.
# produces an error message to that effect.
def createRefMessage (imageFileId,audioFileId,mf):
    if findRefsInMain(imageFileId,audioFileId,mf):
        return "<li>Media File " + mf.filename + " cannot be deleted because it is referenced as the image or audio.</li>"
    else:
        return "<li>Media File " + mf.filename + " cannot be deleted because it is referenced in the statement.</li>"

    # Return True if anything refers to this media file
def getHintMediaRefs (hint, mediaFile):
    mediaFileId= mediaFile.id
    refs = findRefsInMain(hint.imageFile_id, hint.audioFile_id,mediaFile)
    if not refs:
        refs = findRefsInStatementHTML(hint.statementHTML, mediaFile.filename)

    return refs

# given a list of files, upload them to the appropriate directory
# problem media goes in problem_XXX
# hint media goes in problem_XXX/hint_YYY
def uploadFiles (files, probId, hintId=None):
    for f in files:
        pmf=handle_uploaded_file(probId, f, hintId)

# Given the media file ids and the problem/hint, delete them.  Will fail to delete
# media that has an entry in the ProblemMediaFile table that is used in a the Problem.   Returns the list of failures.
def processProblemDeleteMediaFiles (mfIds, problem):
    fails = []
    probId = problem.id
    for mid in mfIds:
        mf = get_object_or_404(ProblemMediaFile,pk=mid)
        refs = getProblemMediaRefs(problem,mf)
        if not refs:
            deleteMediaFile(probId, mf.filename, None)
            mf.delete()
        else:
            fails.append(mf)
    return fails


def processHintDeleteMediaFiles (mfIds, hint):
    fails = []
    for mid in mfIds:
        mf = get_object_or_404(ProblemMediaFile,pk=mid)
        refs = getHintMediaRefs(hint,mf) # see if there are references to this media file in the imageFileiD, audioFileId, or statementHTML
        if not refs:
            deleteMediaFile(None, mf.filename, hint.id)
            mf.delete()
        else:
            fails.append(mf)
    return fails


def produceProblemMediaDeleteMessage (problem, fails):
    if len(fails) == 0:
        return ""
    str = "The following files could not be deleted from the problem: <ul>"
    for f in fails:
        str += createRefMessage(problem.imageFile_id,problem.audioFile_id,f)
    str += "</ul>"
    return str

# Takes a problem or a hint (as pORh) and returns messages for each
# Puts together return JSON that includes remaining media files, media files that are not deleted, and
# messages describing why each file can't be deleted
def produceDeleteResults (p, fails):
    # Get the remaining media files in the problem
    mediaFiles = p.getMediaFiles()
    mfs = [mf.toJSON() for mf in mediaFiles]
    # note: fails is a list of pairs (ProblemMediaFile, list of hints or problem that refers to it)
    nd = [mf[0].toJSON() for mf in fails] # list of media files that can't be deleted
    ndmsgs = []
    for f in fails:
        objs = f[1] # list of objects that refer to the media file
        msg = ""
        for o in objs:
            msg += " Hint " + str(o.id) if isinstance(o,Hint) else " Problem " + str(o.id)
        ndmsgs.append(msg)
    d = {'mediaFiles': mfs, 'notDeleted': nd, 'refs': ndmsgs}
    return d

def save_problem_media (request, probId):
    if request.method == "POST":
        post = request.POST
        p = get_object_or_404(Problem,pk=probId)
        if 'mediaFiles[]' in request.FILES:
            files = request.FILES.getlist('mediaFiles[]')
            uploadFiles(files,probId)
        # deletes are given as an array of ids
        mediaIds = post.getlist('deleteIds[]')
        fails = processProblemDeleteMediaFiles(mediaIds, p)
        msg = produceProblemMediaDeleteMessage(p,fails)
        mfJSON = [mf.toJSON() for mf in p.getMediaFiles()]
        d = {'mediaFiles': mfJSON, 'message': msg}
        return JsonResponse(d)

# URL: POST /problem/<id>/metaInfo
# write the fields into the problem table and return nothing.
def save_problem_meta_info (request, probId):
    if request.method == 'POST':
        post = request.POST
        standardId = post['standardId']
        clusterId = post['clusterId']
        authorNotes = post['authorNotes']
        creator = post['creator']
        lastModifier = post['lastModifier']
        example = post['example']
        usableAsEx = post['usableAsExample']
        try:
            example = int(example)
        except: example = None

        video = post['video']
        try:
            video = int(video)
        except: video = None


        p = get_object_or_404(Problem, pk=probId)
        if 'snapshotFile' in request.FILES:
            file = request.FILES['snapshotFile']
            filename = file.name
            ext = filename.split(".")[1]
            filename = "problem_"+probId+"."+ext
            write_file(SNAPSHOT_DIRNAME, file, filename)
            p.setFields(screenshotURL=filename)

        p.setFields(standardId=standardId,clusterId=clusterId,
                   authorNotes=authorNotes,creator=creator,lastModifier=lastModifier,
                   example=example,video=video, usableAsExample=(usableAsEx == 'True'))
        p.save()

        d = {'message': "Meta info Saved", 'lastWriteTime': p.updated_at}
        return JsonResponse(d)


def getHint (request, hintId):
    h = get_object_or_404(Hint,pk=hintId)
    d = h.toJSON()
    return JsonResponse(d)


# when the user drag and drops the hints to re-order them, we get a post with the new sequence order of ids.
#  This means re-ordering the hints in the db
def saveHints (request, probId):
    if request.method == "POST":
        post = request.POST
        ids = post.getlist('hintIds[]')
        loc = 0
        for i in ids:
            hint = Hint.objects.get(pk=i)
            hint.order = loc
            loc += 1
            hint.save()
        return JsonResponse({});



# Produce a message describing why the media files (pmfs) cannot be deleted from the hint
def produceHintMediaDeleteMessage (hint, pmfs):
    if len(pmfs) == 0:
        return "Saved."
    str= "The following media files cannot be deleted from the hint:<ul>"
    for f in pmfs:
        str += createRefMessage(hint.imageFile_id,hint.audioFile_id,f)
    str += "</ul>"
    return str

# When the user clicks save in the hint dialog this is called with the form inputs
def saveHint (request, probId):
    if request.method == "POST":
        post = request.POST
        id = post['id'] # the hint ID
        # a brand new hint save will have no id.  So create the object now so we have it and its ID
        if not id:
            hints = Hint.objects.filter(problem_id=probId)
            name = 'Hint ' + str(len(hints) + 1)
            order = len(hints)
            h = Hint(name=name,problem_id=probId,order=order)
            h.save()
            id = str(h.id)

        statementHTML = post['statementHTML']
        # hoverText = post['hoverText']
        imageURL = post['imageURL']
        placement = post['himage_placement']
        imgfil = None
        audfil = None

        p = get_object_or_404(Problem,pk=probId)
        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            audResource = "{[" + audFile.name + "]}"
            audfil = handle_uploaded_file(probId, audFile, id)

        # imageFile and imageURL are fields that should not be given at the same time.
        # But it is hard to have the hint dialog enforce this so instead we use this rule:
        # if both are given we ignore the imageURL and use the imageFile.  This makes sense
        # because the imageFile will only be there if the user selected a local file in this current dialog
        # whereas the imageURL might be there from a previous time.

        if 'imageFile' in request.FILES:
            imgFile = request.FILES['imageFile']
            imageURL = "{[" + imgFile.name + "]}"
            imgfil = handle_uploaded_file(probId, imgFile,id)

        if 'givesAnswer' in post:
            givesAnswer = True
        else: givesAnswer = False
        # media files that are being uploaded along with the hint
        if 'hmediaFiles[]' in request.FILES:
            files = request.FILES.getlist('hmediaFiles[]')
            if id:
                uploadFiles(files,probId,id)

        h = get_object_or_404(Hint,pk=id)
        h.statementHTML=statementHTML
        # h.hoverText=hoverText
        h.order=post['order']
        h.imageURL = imageURL
        # If setting the imageURL field, then we eliminate the setting of the imageFile field.
        if imageURL:
            h.imageFile = None
        h.placement=placement
        h.givesAnswer=givesAnswer
        # only write audio filename if an aud file is uploaded.
        if audfil:
            h.audioFile = audfil
            h.audioResource = audResource
        # only write an image file if one is given
        if imgfil:
            h.imageFile=imgfil

        h.save()

    # finally process any delete requests that are included as media file ids
    delHintMediaFileIds = post.getlist('deletehMediaFile[]') # ids of selected media files to delete
    fails = processHintDeleteMediaFiles(delHintMediaFileIds, h) # returns PMF objs that couldn't be deleted
    msg = produceHintMediaDeleteMessage(h,fails) # Produce error message about why media couldn't delete
    json = h.toJSON()
    success = 1 if len(fails) == 0 else 0
    d = {'hint': json, 'success': success, 'message': msg}
    return JsonResponse(d)
    # return redirect("qauth_edit_prob",probId=probId)


def deleteMedia (request, probId):
    if request.method == "POST":
        post = request.POST
        # files are given as an array of ids
        mediaIds = post.getlist('data[]')
        for mid in mediaIds:
            mf = get_object_or_404(ProblemMediaFile,pk=mid)
            deleteMediaFile(probId, mf.filename)
            mf.delete()
    return JsonResponse({})
    # return redirect("qauth_edit_prob",probId=probId)


def getLayouts (request):
    layouts = ProblemLayout.objects.all()
    # create a list of layout objects in json
    a = [l.toJSON() for l in layouts]
    return JsonResponse(a,safe=False)


def getProblemJSON (request, probId):
    p = get_object_or_404(Problem,pk=probId)
    js = p.toJSON()
    return JsonResponse(js,safe=False)

# This doesn't delete the image file.  It just dis-associates the image from the problem.
# If its an imageFile we set the ID to null. If its an imageURL, we set it to null
def removeProblemImage (request, probId):
    if request.method == "DELETE":
        p = get_object_or_404(Problem,pk=probId)
        p.imageURL=None
        p.imageFile=None
        p.save()
    return JsonResponse({})

# This doesn't delete the audio file.  It just dis-associates the audio from the problem.
# We set the audioResource and audioFile to None
def removeProblemAudio (request, probId):
    if request.method == "DELETE":
        p = get_object_or_404(Problem,pk=probId)
        p.audioResource=None
        p.audioFile=None
        p.save()
    return JsonResponse({})

# This doesn't delete the audio file.  It just dis-associates the audio from the hint.
# We set the audioResource and audioFile to None
def removeHintAudio (request, hintId):
    if request.method == "DELETE":
        p = get_object_or_404(Hint,pk=hintId)
        p.audioResource=None
        p.audioFile=None
        p.save()
    return JsonResponse({})

# This doesn't delete files.  It just dis-associates the image from the hint
# by setting the hints imageURL and imageFile to be null
def removeHintImage (request, hintId):
    if request.method == "DELETE":
        h = get_object_or_404(Hint,pk=hintId)
        h.imageURL=None
        h.imageFile=None
        h.save()
    return JsonResponse({})