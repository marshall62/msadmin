from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from msadmin.qa.qauth_model import Problem, ProblemMediaFile, Hint, ProblemLayout
from msadmin.qa.util import handle_uploaded_file, deleteMediaFile


def getMediaRefs (problem, mediaFileId):
    refs = []
    if problem.imageFile and problem.imageFile.id == int(mediaFileId):
        refs.append(problem)
    elif problem.audioFile and problem.audioFile.id == int(mediaFileId):
        refs.append(problem)
    for h in problem.getHints():
        if h.imageFile and h.imageFile.id == int(mediaFileId):
            refs.append(h)
    return refs


def save_problem_media (request, probId):
    if request.method == "POST":
        post = request.POST
        p = get_object_or_404(Problem,pk=probId)
        if 'mediaFiles[]' in request.FILES:
            #files = post.getlist('mediaFiles[]')

            files = request.FILES.getlist('mediaFiles[]')
            for f in files:
                pmf=handle_uploaded_file(probId, f)

        # deletes are given as an array of ids
        # For each id, we check to see if the problem.imageFile or if any of the problems hint.imageFile refers to this same id
        # If so, we return the list of ids that this is true for because this would indicate that the user is trying to delete
        # a media file that is referenced by a hint or the problem which is an error.  We tell the user to first eliminate the
        # reference and then delete the media.
        mediaIds = post.getlist('deleteIds[]')
        fails = []
        for mid in mediaIds:
            mf = get_object_or_404(ProblemMediaFile,pk=mid)
            refs = getMediaRefs(p,mid)
            if len(refs) == 0:
                deleteMediaFile(probId, mf.filename)
                mf.delete()
            else:
                fails.append((mf,refs)) # tuple of (mediaFile, [objects that refer to it])
        mediaFiles = ProblemMediaFile.objects.filter(problem_id=probId)
        mfs = [mf.toJSON() for mf in mediaFiles]
        nd = [mf[0].toJSON() for mf in fails] # list of media files that can't be deleted
        ndmsgs = []
        for f in fails:
            objs = f[1] # list of objects that refer to the media file
            msg = ""
            for o in objs:
                msg += " Hint " + str(o.id) if isinstance(o,Hint) else " Problem " + str(o.id)
            ndmsgs.append(msg)
        d = {'mediaFiles': mfs, 'notDeleted': nd, 'refs': ndmsgs}
        return JsonResponse(d)


def getHint (request, hintId):
    h = get_object_or_404(Hint,pk=hintId)
    d = h.toJSON()
    return JsonResponse(d)


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

# when the user drag and drops the hints to re-order them, we get a post with the new sequence order of ids.
#  This means re-ordering the hints in the db
def saveHint (request, probId):
    if request.method == "POST":
        post = request.POST
        id = post['id']
        statementHTML = post['statementHTML']
        hoverText = post['hoverText']
        imageURL = post['imageURL']
        placement = post['himage_placement']
        audioResource = post['audioResource']
        imgfil = None
        p = get_object_or_404(Problem,pk=probId)
        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            audioResource = audFile.name
            handle_uploaded_file(probId, audFile)
        # imageFile and imageURL are fields that should not be given at the same time.
        # But it is hard to have the hint dialog enforce this so instead we use this rule:
        # if both are given we ignore the imageURL and use the imageFile.  This makes sense
        # because the imageFile will only be there if the user selected a local file in this current dialog
        # whereas the imageURL might be there from a previous time.

        if 'imageFile' in request.FILES:
            imgFile = request.FILES['imageFile']
            imageURL = None
            imgfil = handle_uploaded_file(probId, imgFile)

        if 'givesAnswer' in post:
            givesAnswer = True
        else: givesAnswer = False
        if id:
            h = get_object_or_404(Hint,pk=id)
            h.statementHTML=statementHTML
            h.hoverText=hoverText
            h.order=post['order']
            h.imageURL = imageURL
            h.audioResource= audioResource
            h.placement=placement
            h.givesAnswer=givesAnswer
            # if no file or url is sent up,we dont want to overwrite existing imageFileId settings,
            # but we do allow it to blow away imageURL because this is the only way to reset imageURL.
            if not imgfil and not imageURL:
                res = ProblemMediaFile.objects.filter(problem_id=probId,hint=h) # maybe an existing image file.
                if len(res)>0:
                    imgfil = res[0]
            h.imageFile=imgfil
            h.save()
        else:
            hints = Hint.objects.filter(problem_id=probId)
            name = 'Hint ' + str(len(hints) + 1)
            order = len(hints)
            # Hint names are like Hint 1, Hint 2 ... the order field is 0-based
            h = Hint(name=name,statementHTML=statementHTML,problem_id=probId,audioResource=audioResource,
                     imageURL=imageURL,hoverText=hoverText,order=order,givesAnswer=givesAnswer, placement=placement, imageFile=imgfil)
            h.save()

    json = h.toJSON()
    return JsonResponse(json)
    # return redirect("qauth_edit_prob",probId=probId)


def deleteMedia (request, probId):
    if request.method == "POST":
        post = request.POST
        # hints are given as an array of ids
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