import os
import re
import logging
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseServerError
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from datetime import datetime

from django.db.models import ProtectedError

from msadmin.qa.exc import UserException
from msadmin.qa.util import handle_uploaded_file, deleteProblemAnswers, saveProblemMultiChoices, \
    saveProblemShortAnswers, getProblemDirName
from msadminsite.settings import QUICKAUTH_PROB_DIRNAME, SNAPSHOT_DIRNAME
from .qauth_model import *
from .util import deleteMediaDir, write_file
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

# settings.py has the name of the dir where quickAuth problems should be stored.
QA_DIR=os.path.join(QUICKAUTH_PROB_DIRNAME,"")

# CONTENT_MEDIA_URL = "http://rose.cs.umass.edu/mathspring/mscontent/html5Probs/"

#@staff_member_required   will increase the security of a view function

# Shows the main page of the site
@login_required
def main (request):
    probs = Problem.get_quickAuth_problems()
    return render(request, 'msadmin/qa/qauth_main.html', {'problems': probs})

# Produces a page that has react js but the bootstrap styling doesn't work
def reactTest(request):
    prob = get_object_or_404(Problem, pk=1338)
    return render(request, 'msadmin/react1.html', {'problem': prob})

# support for AJAX call from a checkbox next to a intervention-selector node in the jstree
# It will set the isActive field in the class_sc_is_map table to true or false.
@login_required
def create_problem (request):
    allTopics = Topic.objects.all()
    return render(request, 'msadmin/qa/qauth_edit.html', {'probId': -1, 'problem': None, 'hints': None, 'allTopics': allTopics, 'errors': False, 'message': None, 'qaDir': QA_DIR, 'SNAPSHOT_DIRNAME': SNAPSHOT_DIRNAME})

def getTopics (prob):
    allTopics = Topic.objects.all()
    # get the topics by filtering such that we look find the connected map with the given problem
    inTopics = Topic.objects.filter(problemtopicmap__problem=prob)
    if inTopics.count() > 0:
        for t1 in inTopics:
            for t2 in allTopics:
                if t1.id == t2.id:
                    t2.setSelected(True)
    return allTopics, inTopics

@login_required
def edit_problem (request, probId):
    prob = get_object_or_404(Problem, pk=probId)
    logger.debug("Editing QA problem " +  probId)
    hints = Hint.objects.filter(problem=prob).order_by('order')
    allTopics,inTopics = getTopics(prob)

    return render(request, 'msadmin/qa/qauth_edit.html', {'probId': probId, 'problem': prob, 'hints': hints, 'allTopics': allTopics, 'errors': False, 'message': None, 'qaDir': QA_DIR, 'SNAPSHOT_DIRNAME': SNAPSHOT_DIRNAME})

# write the file to path/problem_probId/f.name
# no longer used.  We use the handle_uploaded_file above instead
@login_required
def saveMedia(probId, name, file):
    # Get the default FileSystemStorage class based on MEDIA_ROOT settings in settings.py
    fs = FileSystemStorage()
    location = fs.location
    file_permissions_mode = fs.file_permissions_mode
    directory_permissions_mode = fs.directory_permissions_mode
    newPath = os.path.join(location, getProblemDirName(probId))
    # MEDIA_ROOT (on the server) is the location of the mscontent/html5Problems directory within the Apache
    # server.   This creates a directory in there with the name of the problem (or proceeds if it exists).
    try:
        os.mkdir(newPath)
    except FileExistsError as e:
        pass

    newloc = os.path.join(location, getProblemDirName(probId), name)
    # Create a new FileSystemStorage object based on the default one.  It uses the new directory for the problem.
    fs2 = FileSystemStorage(location=newloc , file_permissions_mode=file_permissions_mode,directory_permissions_mode=directory_permissions_mode)
    if fs2.exists(file.name):
        fs2.delete(file.name)
    fs2.save(file.name, file)

def getLoggedInUsername():
    return "dave"

@login_required
def save_problem (request):
    if request.method == "POST":
        post = request.POST
        id = post['id']
        logger.debug("Saving QA problem " +  id)
        name = post['name']
        nickname = post['nickname']
        statementHTML = post['statementHTML']
        # answer = post['answer']
        if 'imageURL' in post:
            imageURL = post['imageURL']
        else:
            imageURL = None
        if 'status' in post:
            status = post['status']
        else:
            status = None
        if 'difficulty' in post:
            initDifficulty = post['difficulty']
        else:
            initDifficulty = -1
        if 'questType' in post:
            questType = post['questType']
        else:
            questType = None
        problemFormat = post['problemFormat']
        correctAnswer=None
        if questType == Problem.MULTI_CHOICE:
            correctAnswer = post['correctChoice']
            choices = post.getlist('multichoice[]')
        else:
            answers = post.getlist('shortanswer[]')
            correctAnswer = None # want all the answers to go into the problemAnswers table - not into problem.answer
        audioResource = post['audioResource']
        if 'layout' in post:
            layoutTemplateId = post['layout']
        else: layoutTemplateId = None
        # authorNotes = post['authorNotes']
        # creator = post['creator']
        # lastModifier = post['lastModifier']
        # example = post['example']
        # try:
        #     example = int(example)
        # except: example = None
        #
        # video = post['video']
        # try:
        #     video = int(video)
        # except: video = None

        audioResource = 'question' if audioResource == 'hasAudio' else None
        form= 'quickAuth'
        # If an image file is uploaded, create a new imageURL of {[filename.jpg]}
        if 'imageFile' in request.FILES:
            imgFile = request.FILES['imageFile']
            imageURL = '{[' + imgFile.name + ']}'
        # if an audio file is uploaded create a new audioResource of {[sound.mp3]}
        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            audioResource= '{['+audFile.name+']}'

        # user = getLoggedInUsername()
        uname = request.user.username
        if not id:
            now = datetime.now()
            # We can't rely on mysql CURRENT_TIME to work on the created_at field because it is old version of MySQL
            # not supporting two columns with CURRENT_TIME defaults.  So set it manually and let the lastModTime be
            # handled automatically
            p = Problem(name=name,nickname=nickname,statementHTML=statementHTML,answer=correctAnswer,
                        imageURL=imageURL,status=status,form=form, problemFormat=problemFormat,
                        questType=questType, audioResource=audioResource, layout_id=layoutTemplateId,
                        creator=uname,lastModifier=uname,created_at=now)
            p.save()
            if initDifficulty != -1:
                insertProblemDifficulty(str(p.pk),initDifficulty)

        else:
            p = get_object_or_404(Problem, pk=id)
            p.setFields(name=name,nickname=nickname,statementHTML=statementHTML,answer=correctAnswer,
                        status=status,form=form, problemFormat=problemFormat,
                        questType=questType, layout_id=layoutTemplateId,lastModifier=uname)
            if initDifficulty != -1 and selectProblemDifficulty(id):
                updateProblemDifficulty(id,initDifficulty)
            elif initDifficulty != -1:
                insertProblemDifficulty(id,initDifficulty)

            # if imageURL is given set it and clear the problem imagefile
            if imageURL:
                p.imageURL=imageURL
                p.imageFile=None
            if audioResource:
                p.audioResource=audioResource
        p.save()
        probId = p.pk

        if 'imageFile' in request.FILES:
            imgFile = request.FILES['imageFile']
            pmf = handle_uploaded_file(probId, imgFile)
            p.imageFile=pmf
            p.save()
            # saveMedia(probId, imgFile.name, imgFile)


        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            af = handle_uploaded_file(probId, audFile)
            p.audioFile = af
            p.save()

        # if its a multichoice problem delete all the problem answers and add the given list
        if questType==Problem.MULTI_CHOICE:
            deleteProblemAnswers(p)
            saveProblemMultiChoices(p, correctAnswer, choices)
        else:
            deleteProblemAnswers(p)
            saveProblemShortAnswers(p, correctAnswer, answers)
        # return redirect("qauth_edit_prob",probId=probId)
        hints = Hint.objects.filter(problem=p).order_by('order')
        msg = validateMediaRefs(p)
        errors = True
        if not msg:
            msg = 'Saved successfully'
            errors = False
        allTopics,inTopics = getTopics(p)
        return render(request, 'msadmin/qa/qauth_edit.html', {'message': msg, 'errors': errors, 'probId': p.id, 'problem': p, 'hints': hints, 'allTopics': allTopics, 'qaDir': QA_DIR, 'SNAPSHOT_DIRNAME': SNAPSHOT_DIRNAME})

# Make sure that the refs in the statement only refer to files that are among the problems media files in the problemmediafile
def validateMediaRefs (problem):
    mediaFiles = problem.getMediaFiles()
    p = r'\{\[(.*?)\]\}'
    match = re.findall(p,problem.statementHTML)
    unresolved = []
    for ref in match:
        found = False
        for f in mediaFiles:
            if ref.strip() == f.filename:
                found = True
                break
        if not found:
            unresolved.append(ref)
    if len(unresolved) > 0:
        s = "Warning: The following media files were referenced in the statement but are not uploaded in the media files section: <ul style='color: red'>"
        for f in unresolved:
            s += "<li>" + f + "</li>"
        s += "</ul>"
        return s
    return None

@login_required
#TODO hint deletion often fails because the hint still refers to media files which must be deleted first.
#If this exception happens django automatically keeps the user in the problem form and pops up an error dialog.   But
# a better result would be to catch the ProtectedError and send the user a message that the deletion fails because media has to be
# cleaned out first.
def deleteHints (request, probId):
    if request.method == "POST":
        post = request.POST
        # hints are given as an array of ids
        hintIds = post.getlist('data[]')
        try:
            for hid in hintIds:
                h = get_object_or_404(Hint,pk=hid)
                h.delete()
                # delete all the rows in the PMF for this hint
                # TODO see msadmin.log.   If trying to delete a hint from the problem this will fail because
                # of the media files.   Should we do the delete and automatically delete the media files?
                mfs = ProblemMediaFile.objects.filter(problem_id=probId, hint_id=hid)
                for f in mfs:
                    f.delete()
                # Blow away all the files in the hint dir and then delete the dir.
                deleteMediaDir(probId,hid)
            # after deleting there may be holes in the ordering sequence, so we renumber all the remaining hints
            # 1-based ordering is used
            hints = Hint.objects.filter(problem_id=probId).order_by('order')
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
            return HttpResponseServerError(message)
    return redirect("qauth_edit_prob",probId=probId)


def updateProblemDifficulty (probId, diffSetting):
    difflev = int(diffSetting) * 0.1
    with connection.cursor() as cursor:
        cursor.execute("UPDATE overallprobdifficulty SET diff_level = %s WHERE problemId = %s", [difflev, probId])


def insertProblemDifficulty (probId, diffSetting):
    difflev = int(diffSetting) * 0.1
    with connection.cursor() as cursor:
        cursor.execute("INSERT into overallprobdifficulty (problemId, diff_level) VALUES (%s, %s)", [probId, difflev])


def selectProblemDifficulty (probId):
    with connection.cursor() as cursor:
        cursor.execute("select diff_level from overallprobdifficulty where problemId= %s", [probId])
        row = cursor.fetchone()
        if row:
            return row[0]
        else: return None


def logDebugTest():
    logger.debug("this is a debug message!")

def logErrorTest():
    logger.error("this is an error message!!")





