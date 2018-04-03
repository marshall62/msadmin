from django.http import JsonResponse
from collections import OrderedDict
from django.shortcuts import get_object_or_404
from msadminsite.settings import SNAPSHOT_DIRNAME
from .util import  write_file
import re

from msadmin.qa.qauth_model import Problem, ProblemMediaFile, Hint, FormatTemplate, Standard, Topic, ProblemTopicMap
from msadmin.qa.util import handle_uploaded_file, deleteMediaFile
from django.contrib.auth.decorators import login_required

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

@login_required
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
@login_required
def save_problem_meta_info (request, probId):
    if request.method == 'POST':
        post = request.POST
        grade = post['stdGrade']
        cluster = post['stdCluster']
        category = post['stdCategory']
        group = post['stdGroup']
        # standardId = post['standardId']
        # clusterId = post['clusterId']
        authorNotes = post['authorNotes']
        creator = post['creator']
        lastModifier = post['lastModifier']
        example = post['example']
        topicIDs = None
        if 'topic' in post:
            topicIDs = post.getlist('topic')
        usableAsEx = post['usableAsExample']

        try:
            example = int(example)
        except: example = None

        video = post['video']
        try:
            video = int(video)
        except: video = None
        addMsg = ""

        if grade not in ["---", 'undefined'] and cluster not in ["---", 'undefined'] and category not in ["---", 'undefined']:
            standardId = grade+"."+cluster+"."+category
            if group not in ["---", 'undefined']:
                standardId += "." + group
        else:
            standardId = None


        foundStd = Standard.objects.filter(id=standardId)
        if not foundStd:
            givenStd = (grade+"."+cluster+"."+category+"."+group).replace("undefined",'---')
            addMsg = "Standard ID " + givenStd + " is not valid"

        p = get_object_or_404(Problem, pk=probId)
        if 'snapshotFile' in request.FILES:
            file = request.FILES['snapshotFile']
            filename = file.name
            ext = filename.split(".")[1]
            filename = "problem_"+probId+"."+ext
            write_file(SNAPSHOT_DIRNAME, file, filename)
            # p.setFields(screenshotURL=filename)

        p.setFields(standardId=standardId,
                   authorNotes=authorNotes,creator=creator,lastModifier=lastModifier,
                   example=example,video=video, usableAsExample=(usableAsEx == 'True'))
        p.save()

        if topicIDs:
            inTopics = ProblemTopicMap.objects.filter(problem=p)
            oldTopicSet = set()
            curTopicSet = set()
            if inTopics.count() > 0:
                for t in inTopics:
                        oldTopicSet.add(t.topic_id)
            for t in topicIDs:
                curTopicSet.add(int(t))
            topicsToRemove = oldTopicSet - curTopicSet
            for t in topicsToRemove:
                m = ProblemTopicMap.objects.filter(topic_id=t,problem=p).first()
                m.delete()
            topicsToAdd = curTopicSet - oldTopicSet
            for t in topicsToAdd:
                m = ProblemTopicMap(topic_id=t,problem=p)
                m.save()

        d = {'message': "Meta info Saved. " + addMsg, 'lastWriteTime': p.updated_at}
        return JsonResponse(d)

@login_required
def getHint (request, hintId):
    h = get_object_or_404(Hint,pk=hintId)
    d = h.toJSON()
    return JsonResponse(d)


# when the user drag and drops the hints to re-order them, we get a post with the new sequence order of ids.
#  This means re-ordering the hints in the db
@login_required
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
        return ""
    str= "The following media files cannot be deleted from the hint:<ul>"
    for f in pmfs:
        str += createRefMessage(hint.imageFile_id,hint.audioFile_id,f)
    str += "</ul>"
    return str

# When the user clicks save in the hint dialog this is called with the form inputs
@login_required
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
    mediaDelMsg = produceHintMediaDeleteMessage(h,fails) # Produce error message about why media couldn't delete
    hintSaveMsg = validateMediaRefs(h)
    json = h.toJSON()
    success = 1 if len(fails) == 0 and not hintSaveMsg else 0
    if not hintSaveMsg:
        hintSaveMsg = "Saved"
    d = {'hint': json, 'success': success, 'message': mediaDelMsg, 'saveMessage': hintSaveMsg}
    return JsonResponse(d)
    # return redirect("qauth_edit_prob",probId=probId)


# Make sure that the refs in the statement only refer to files that are among the problems media files in the problemmediafile
def validateMediaRefs (hint):
    mediaFiles = hint.getMediaFiles()
    p = r'\{\[[ ]*([^,]*?)[ ]*\]\}'
    q = r'\{\[[ ]*([^,]*?)[ ]*,.*?\]\}'
    r = p + '|' + q
    match = re.findall(r,hint.statementHTML)
    # results are a list of of tuples like [('', 'blee.jpg'), ('bar.jpg', ''), ...]
    unresolved = []
    for ref in match:
        found = False
        ref = ref[0] if ref[0] != '' else ref[1]
        for f in mediaFiles:
            if ref == f.filename:
                found = True
                break
        if not found:
            unresolved.append(ref)
    if len(unresolved) > 0:
        s = "Saved.<br>Warning: The following media files were referenced in the statement but are not uploaded in the media files section: <ul style='color: red'>"
        for f in unresolved:
            s += "<li>" + f + "</li>"
        s += "</ul>"
        return s
    return None

@login_required
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

@login_required
def getLayouts (request):
    layouts = FormatTemplate.objects.all()
    # create a list of layout objects in json
    a = [l.toJSON() for l in layouts]
    return JsonResponse(a,safe=False)

# A standard is GRADE.CLUSTER.CATEGORY[.GROUP]
#
# Builds a dictionary like:
# {"1": {"G": {"RED": ["1", "2"], "BLUE": [], "GREEN": ["1","2.a", "2.b"]} "NS": {"YELLER": [], "ORANGE": []}},
#  "2": {"G": {"RED": ["1", "2"], "BLUE": [], "GREEN": ["1","2.a", "2.b"]} "NS": {"YELLER": [], "ORANGE": []}},
# ...
#   "K" ...
#   "H" ....
# }
def getStandardDict ():
    stds = Standard.objects.all().order_by('grade', 'id')
    stdDict = OrderedDict()
    for std in stds:
        id = std.id
        grade = std.grade
        idx = id.split('.')
        if len(idx) >= 3:
            # Create a standard code that doesn't have the grade in it.
            if grade.lower() == 'h':
                code = std.id
            else:
                code = std.id[2:]
            if not grade in stdDict:
                stdDict[grade] = OrderedDict()
            codex = code.split('.')
            clusterDict = stdDict[grade]
            cluster = codex[0]
            if not cluster in clusterDict:
                clusterDict[cluster] = OrderedDict()
            catDict = clusterDict[cluster]
            cat = codex[1]
            catDict[cat] = []
            # THe group level is optional.  Will be an empty list if no groups for this category
            if len(codex) > 2:
                catDict[cat].append('.'.join(codex[2:]))

    return stdDict

'''
Convert the OrderedDict to a list of lists like:
[ [1, [gr1-clusters]],
  [2, [....]]
]
[gr1-clusters] is
[[G, [G-cats]], [MD, [MD-cats]] ...]

[G-cats] is
[[RED, []], [BLUE, [1,2.a,2.b]] ...]
'''
def convertDictToLists (standardsDict):
    l = []
    for grade in standardsDict:
        v = standardsDict[grade] # v is a dict with clusters as keys
        a = [grade, []]
        l.append(a)
        for cluster in v:
            v2 = v[cluster] # v2 is a dict with categories as keys
            b = [cluster, []]
            a[1].append(b)
            for cat in v2:
                v3 = v2[cat] # v3 is a list of groups - it may be empty
                c = [cat,v3]
                b[1].append(c)

    return l



@login_required
def getStandards (request):
    stds = getStandardDict()
    stdl = convertDictToLists(stds)
    return JsonResponse(stdl,safe=False)

@login_required
def getProblemJSON (request, probId):
    p = get_object_or_404(Problem,pk=probId)
    js = p.toJSON()
    return JsonResponse(js,safe=False)

# This doesn't delete the image file.  It just dis-associates the image from the problem.
# If its an imageFile we set the ID to null. If its an imageURL, we set it to null
@login_required
def removeProblemImage (request, probId):
    if request.method == "DELETE":
        p = get_object_or_404(Problem,pk=probId)
        p.imageURL=None
        p.imageFile=None
        p.save()
    return JsonResponse({})

# This doesn't delete the audio file.  It just dis-associates the audio from the problem.
# We set the audioResource and audioFile to None
@login_required
def removeProblemAudio (request, probId):
    if request.method == "DELETE":
        p = get_object_or_404(Problem,pk=probId)
        p.audioResource=None
        p.audioFile=None
        p.save()
    return JsonResponse({})

# This doesn't delete the audio file.  It just dis-associates the audio from the hint.
# We set the audioResource and audioFile to None
@login_required
def removeHintAudio (request, hintId):
    if request.method == "DELETE":
        p = get_object_or_404(Hint,pk=hintId)
        p.audioResource=None
        p.audioFile=None
        p.save()
    return JsonResponse({})

# This doesn't delete files.  It just dis-associates the image from the hint
# by setting the hints imageURL and imageFile to be null
@login_required
def removeHintImage (request, hintId):
    if request.method == "DELETE":
        h = get_object_or_404(Hint,pk=hintId)
        h.imageURL=None
        h.imageFile=None
        h.save()
    return JsonResponse({})