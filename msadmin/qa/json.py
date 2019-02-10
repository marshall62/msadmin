from django.db import connection
from django.db.models import ProtectedError
from django.http import JsonResponse
from collections import OrderedDict
from django.shortcuts import get_object_or_404, redirect
from msadminsite.settings import SNAPSHOT_DIRNAME
from .util import  write_file, deleteMediaDir, deleteProblemDir
import re,os,sys
from datetime import datetime

from msadmin.qa.qauth_model import Problem, ProblemMediaFile, Hint, FormatTemplate, Standard, Topic, ProblemTopicMap, \
    Cluster, ProblemStandardMap, ProblemDifficulty, ProblemAnswer, ProblemLayout
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


def processCCSS (prob, grades,domains,clusters,standards,parts):
    addMsg = ""
    errors = False
    count = 0
    probStdIds = []
    for grade,domain,cluster,standard,part in zip(grades,domains,clusters,standards,parts):
        if grade not in ["---", 'undefined'] and domain not in ["---", 'undefined']  and cluster not in ["---", 'undefined'] and standard not in ["---", 'undefined']:
            if grade != 'H':
                standardId = grade+"."+domain+"."+cluster+"."+standard
                catCode = grade+"."+domain
                clustABCD = cluster
            else:
                standardId = domain+"."+cluster+"."+standard
                catCode = domain+"."+cluster
                clustABCD = standard
            if part not in ["---", 'undefined']:
                standardId += "." + part
        else:
            standardId = None

        foundStd = Standard.objects.filter(idABC=standardId)
        if not foundStd.exists() or foundStd.count() == 0:
            givenStd = (grade+"."+domain+"."+cluster+"."+standard+"."+part).replace("undefined",'---')
            addMsg += "Standard ID " + givenStd + " is not valid<br>"
            errors = True
            stdId = None
            clustId = None
        else:
            foundStd = foundStd.first()
            stdId = foundStd.id
            clust = Cluster.objects.filter(categoryCode=catCode, clusterABCD=clustABCD)
            if clust.count() > 0:
                clustId = clust.first().id
            else:
                clustId = None
        # The first CCSS is considered the primary and we need to set the problems standard and cluster Ids.
        if count == 0:
            prob.setFields(standardId=stdId,clusterId=clustId)
        # Every CCSS should be entered into the problemStandardMap
        if stdId:
            probStdIds.append(stdId)

        count += 1
    if errors:
        return errors, addMsg
    # Go through the ProblemStandardMap and delete any standards that are no longer in the list
    # and add (or update the modtimestamp) of standards that are in the list.
    pstd = ProblemStandardMap.objects.filter(probId=prob.pk)
    if pstd.exists():
        for m in pstd:
            # If the map row already exists remove it from list of standards
            if m.stdId in probStdIds:
                probStdIds.remove(m.stdId)
            # delete a map if its not in the list being sent by the gui
            else:
                m.delete()
    # The remaining standards in probStds will be newly added ones
    for ps in probStdIds:
        psm = ProblemStandardMap(probId=prob.pk, stdId=ps)
        psm.save()

    return errors, addMsg

# URL: POST /problem/<id>/metaInfo
# write the fields into the problem table and return nothing.
@login_required
def save_problem_meta_info (request, probId):
    if request.method == 'POST':
        post = request.POST
        grades = post.getlist('stdGrade')
        domains = post.getlist('stdDomain')
        clusters = post.getlist('stdCluster')
        standards = post.getlist('stdStandard')
        parts = post.getlist('stdPart')
        # standardId = post['standardId']
        # clusterId = post['clusterId']
        authorNotes = post['authorNotes']
        creator = post['creator']
        lastModifier = request.user.username
        example = post['example']
        hasSnapshot = 'hasSnapshot' in post or 'snapshotFile' in request.FILES
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
        p = get_object_or_404(Problem, pk=probId)
        errs, addMsg = processCCSS(p,grades,domains,clusters,standards,parts)

        if 'snapshotFile' in request.FILES:
            ss_file = request.FILES['snapshotFile']
            filename = p.getSnapshotFilename()
            write_file(SNAPSHOT_DIRNAME, ss_file, filename)

        now = datetime.now()
        p.setFields(authorNotes=authorNotes,creator=creator,lastModifier=lastModifier, updated_at=now,
                   example=example,video=video, usableAsExample=(usableAsEx == 'True'), hasSnapshot=hasSnapshot)
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
                # insertProblemTopic(p.id, t)
                m = ProblemTopicMap(topic_id=t,problem=p)
                m.save()

        d = {'message': "Meta info Saved. " + addMsg, 'lastWriteTime': p.updated_at}
        return JsonResponse(d)


# Put a row in the Problem-Topic mapping table (for some reason I need to do this rather than work with the model ProblemTopicMap object which has errors when I create and save)
def insertProblemTopic (probId,topicId):
    with connection.cursor() as cursor:
        q = '''INSERT into probprobgroup (probId,pgroupId)
          VALUES (%s,%d)''' % (probId, topicId)
        cursor.execute(q)


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
def saveHint(request, probId):
    if request.method == "POST":
        post = request.POST
        hint_id = post['id']  # the hint ID
        # a brand new hint save will have no hint_id.  So create the object now so we have it and its ID
        if not hint_id:
            hints = Hint.objects.filter(problem_id=probId)
            name = 'Hint ' + str(len(hints) + 1)
            order = len(hints)
            h = Hint(name=name,problem_id=probId, order=order)
            h.save()
            hint_id = str(h.id)
        else:
            h = get_object_or_404(Hint, pk=hint_id)

        statementHTML = post['statementHTML']
        # hoverText = post['hoverText']
        imageURL = post['imageURL']
        audResource = None
        placement = post['himage_placement']
        imgfil = None
        audfil = None

        h.statementHTML = statementHTML
        # h.hoverText=hoverText
        h.order = post['order']

        # p = get_object_or_404(Problem, pk=probId)
        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            audResource = "{[" + audFile.name + "]}"
            audfil = handle_uploaded_file(probId, audFile, hint_id)

        # imageFile and imageURL are fields that should not be given at the same time.
        # But it is hard to have the hint dialog enforce this so instead we use this rule:
        # if both are given we ignore the imageURL and use the imageFile.  This makes sense
        # because the imageFile will only be there if the user selected a local file in this current dialog
        # whereas the imageURL might be there from a previous time.

        if h.imageFile is None and not 'imageFile' in request.FILES:
            # No new image exists, no new image has been added, so it might be an added or changed imageURL
            imageURL = imageURL if imageURL else h.imageURL
        else:
            if 'imageFile' in request.FILES:
                # New file added and do everything based on this file
                imgFile = request.FILES['imageFile']
                image_file_name = imgFile.name
                imgfil = handle_uploaded_file(probId, imgFile, hint_id)
            else:
                # No new image added, but an older image exists, which might have been changed
                image_file_name = h.imageFile.filename

            if placement == '1':
                # For "replace problem figure", the DB field for imageURL needs to be populated
                imageURL = "{[" + image_file_name + "]}"
            elif placement == '2':
                # For "inside hint", the DB field for imageURL needs to be cleared
                imageURL = ""
            else:
                raise Exception('Invalid value for placement - {}'.format(placement))

        h.imageURL = imageURL
        h.placement = placement

        gives_answer = 'givesAnswer' in post
        h.givesAnswer = gives_answer

        # media files that are being uploaded along with the hint
        if 'hmediaFiles[]' in request.FILES:
            files = request.FILES.getlist('hmediaFiles[]')
            if hint_id:
                uploadFiles(files, probId, hint_id)

        # only write audio filename if an aud file is uploaded.
        if audfil:
            h.audioFile = audfil
            h.audioResource = audResource
        # only write/update an image file if one is given
        if imgfil:
            h.imageFile = imgfil

        h.save()

        # finally process any delete requests that are included as media file ids
        delHintMediaFileIds = post.getlist('deletehMediaFile[]')  # ids of selected media files to delete
        fails = processHintDeleteMediaFiles(delHintMediaFileIds, h)  # returns PMF objs that couldn't be deleted
        mediaDelMsg = produceHintMediaDeleteMessage(h, fails)  # Produce error message about why media couldn't delete
        hintSaveMsg = validateMediaRefs(h)
        json = h.toJSON()
        success = 1 if len(fails) == 0 and not hintSaveMsg else 0
        if not hintSaveMsg:
            hintSaveMsg = "Saved"
        d = {'hint': json, 'success': success, 'message': mediaDelMsg, 'saveMessage': hintSaveMsg}
        return JsonResponse(d)
    else:
        return redirect("qauth_edit_prob", probId=probId)


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
    stds = Standard.objects.all().order_by('grade', 'idABC')
    d = OrderedDict()
    for std in stds:
        id = std.idABC
        grade = std.grade
        idx = id.split('.')
        if len(idx) >= 4:
            # Create a standard code that doesn't have the grade in it.
            if grade.lower() == 'h':
                code = std.idABC
            else:
                code = std.idABC[2:]
            if not grade in d:
                d[grade] = OrderedDict()
            codex = code.split('.')
            domainDict = d[grade]
            domain = codex[0]
            if not domain in domainDict:
                domainDict[domain] = OrderedDict()
            clusterDict = domainDict[domain]
            cluster = codex[1]
            if not cluster in clusterDict:
                clusterDict[cluster] = OrderedDict()
            stdDict = clusterDict[cluster]
            std = codex[2]
            if std not in stdDict:
                stdDict[std] = []
            if len(codex) > 3:
                stdDict[std].append('.'.join(codex[3:]))

    return d

'''
Convert the OrderedDict to a list of lists like:
[ [1, [gr1-domains]],
  [2, [....]]
]
[gr1-domains] is
[[G, [G-clusters]], [MD, [MD-clusters]] ...]

[G-clusters] is
[[RED, [[A, [1,2]], [B, [1.a, 1.b]]]], [BLUE, ...
'''
def convertDictToLists (dict):
    l = []
    for grade in dict:
        domainDict = dict[grade] # v is a dict with domains as keys
        a = [grade, []]
        l.append(a)
        for domain in domainDict:
            clusterDict = domainDict[domain] # v2 is a dict with clusters as keys
            b = [domain, []]
            a[1].append(b)
            for cluster in clusterDict:
                stdDict = clusterDict[cluster] # v3 is a dict with stds as keys
                c = [cluster, []]
                b[1].append(c)
                for std in stdDict:
                    d = [std, stdDict[std]]
                    c[1].append(d)

    return l



@login_required
def getStandards (request, probId):
    stds = getStandardDict()
    stdl = convertDictToLists(stds)
    res = {'allStandards': stdl}

    if probId == '-1':
        return JsonResponse(res)

    p = get_object_or_404(Problem,pk=probId)
    pstd_id = p.standardId
    if pstd_id:
        primaryStd = get_object_or_404(Standard,pk=pstd_id)
    else:
        primaryStd = None
    stdlist = []
    otherProbStds = ProblemStandardMap.objects.filter(probId=probId)
    if otherProbStds.exists() and otherProbStds.count() > 0:
        for os in otherProbStds:
            s = get_object_or_404(Standard,pk=os.stdId)
            # don't put the primary standard in the list of other standards
            if s.pk != primaryStd.pk:
                stdlist.append(s.toJSON())
    if primaryStd:
        res['primaryStandard'] = primaryStd.toJSON()
    if len(stdlist) > 0:
        res['probStandards'] = stdlist
    return JsonResponse(res)

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

# Given a problem id and a list of hint ids, delete the hints from the problem.
# The force=True/False flag will force it to delete the hints and ProblemMediaFiles associated with those hints.
# Will return True/False depending on whether it couldn't do the delete based on ProblemMediaFiles .  A second
# message argument is included that reports the filenames of the intruding media files.
def deleteHints (pid, listOfHintIds, force=False):
    hintIds = listOfHintIds
    try:
        for hid in hintIds:
            # If forcing, first eliminate the hint.imageFile and hint.audioFile values which ref the ProblemMediaTable
            if force:
                h = get_object_or_404(Hint,pk=hid)
                h.imageFile = None
                h.audioFile = None
                h.save()
                # Now blow away all the media files that are associated with the hint.
                mfs = ProblemMediaFile.objects.filter(problem_id=pid, hint_id=hid)
                for f in mfs:
                    f.delete()
            # Blow away all the files in the hint dir and then delete the dir.
            h = get_object_or_404(Hint,pk=hid)

            deleteMediaDir(pid,hid)

            h.delete()

        # after deleting there may be holes in the ordering sequence, so we renumber all the remaining hints
        # 1-based ordering is used
        hints = Hint.objects.filter(problem_id=pid).order_by('order')
        for i in range(len(hints)):
            hints[i].order = i+1
            if not hints[i].givesAnswer:
                hints[i].name = 'Hint ' + str(i+1);
            hints[i].save()
    except ProtectedError as e:
        files = e.protected_objects
        names = ""
        for f in files:
            names += f.filename + "\n"

        message = "\nThese media files are blocking hints from deletion:\n " + names
        message += "\n\nCannot delete the hint because it is using media that must be deleted first.  \nPlease edit the hint and delete its media first!\n\n\n"
        return False, message
    return True, None


def deleteProblem (problem):
    try:
        hints = problem.getHints()
        hintIds = [h.pk for h in hints]
        deleteHints(problem.pk, hintIds, True)
        diff = ProblemDifficulty.objects.filter(problem=problem)
        if diff.count() > 0:
            diff[0].delete()
        ans = ProblemAnswer.objects.filter(problem=problem)
        if ans.count() > 0:
            for a in ans:
                a.delete()
        removeClassOmittedProblem(problem.id)
        # eliminate refs to ProblemMediaFiles
        problem.imageFile = None
        problem.audioFile = None
        problem.save()
        media = ProblemMediaFile.objects.filter(problem=problem)
        # blow away all the media files associated with the problem.  Note the hints belonging to the problem
        # already had their media file rows deleted.
        for m in media:
            m.delete()
        deleteProblemDir(problem.id)
        topics = ProblemTopicMap.objects.filter(problem=problem)
        for t in topics:
            t.delete()
        standards =  ProblemStandardMap.objects.filter(probId=problem.id)
        for s in standards:
            s.delete()
        problem.delete()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

# Determine if a problem has been used (for the purpose of disallowing removal)
def probUsed (probId):
    with connection.cursor() as cursor:
        cursor.execute('''SELECT n FROM probstats WHERE probId=%s;''' % (probId))
        r = cursor.fetchone()
        return True if r else False


@login_required
def deleteProblems (request):
    complete = True
    message = None
    if request.method == "POST":
        post = request.POST
        pids = post.getlist('problemsToDelete')
        message = ""
        for pid in pids:
            prob = get_object_or_404(Problem, pk=pid)
            if not probUsed(pid):
                pass
            else:
                complete = False
                message += "Cannot delete problem " + pid + " because it has been used by students\n"
        if not complete:
            return JsonResponse({'complete': complete, 'message': message})

        for pid in pids:
            prob = get_object_or_404(Problem, pk=pid)
            deleteProblem(prob)
    # if any problem cannot be deleted, complete will be returned as False so the user is notified that this cannot be done.
    return JsonResponse({'complete': True, 'message': "Problems successfully deleted."})


@login_required
def bugfix(request):
    for hint_id in ('7105', '7109', '7337', '7479', '7480', '7484', '7523', '7582', '7584', '7585', '7587', '7589',
                    '7636', '7637', '7638', '7639', '7640', '7646', '7647', '7866', '7867', '7868', '7869', '7870',
                    '7887', '7888', '7889', '7905', '7906', '8052', '8081', '8082', '8404', '8424', '8464', '8647',
                    '8648', '8649', '8650', '8651', '8710', '8714', '8715', '8717', '8736', '8737', '8775', '8784'):
        try:
            h = get_object_or_404(Hint, pk=hint_id)
            if h.imageFile:
                h.imageURL = "{[" + h.imageFile.filename + "]}"
                h.save()
        except Exception as e:
            print(e, hint_id)
    return JsonResponse({'status': 'success'})


# grade will be 0-9, diffSetting will be 0 - 9
def removeClassOmittedProblem (probId):
    with connection.cursor() as cursor:
        q = '''DELETE FROM classomittedproblems where probId=%s ''' % (probId)
        cursor.execute(q)
