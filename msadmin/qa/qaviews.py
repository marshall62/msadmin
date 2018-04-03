import os
import re
from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from datetime import datetime

from django.db import connection
from msadmin.qa.util import handle_uploaded_file, deleteProblemAnswers, saveProblemMultiChoices, \
    saveProblemShortAnswers, getProblemDirName
from msadminsite.settings import QUICKAUTH_PROB_DIRNAME, SNAPSHOT_DIRNAME
from .qauth_model import *
from .util import deleteMediaDir, write_file
from django.contrib.auth.decorators import login_required
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
    return render(request, 'msadmin/qa/qauth_edit.html', {'probId': -1, 'qaDir': QA_DIR})

@login_required
def edit_problem (request, probId):
    prob = get_object_or_404(Problem, pk=probId)
    hints = Hint.objects.filter(problem=prob).order_by('order')
    allTopics = Topic.objects.all()
    # get the topics by filtering such that we look find the connected map with the given problem
    inTopics = Topic.objects.filter(problemtopicmap__problem=prob)
    if inTopics.count() > 0:
        for t1 in inTopics:
            for t2 in allTopics:
                if t1.id == t2.id:
                    t2.setSelected(True)
    return render(request, 'msadmin/qa/qauth_edit.html', {'probId': probId, 'problem': prob, 'hints': hints, 'allTopics': allTopics, 'qaDir': QA_DIR, 'SNAPSHOT_DIRNAME': SNAPSHOT_DIRNAME})

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
        name = post['name']
        nickname = post['nickname']
        statementHTML = post['statementHTML']
        # answer = post['answer']
        imageURL = post['imageURL']
        status = post['status']
        initDifficulty = post['difficulty']

        questType = post['questType']
        problemFormat = post['problemFormat']
        correctAnswer=None
        if questType == Problem.MULTI_CHOICE:
            correctAnswer = post['correctChoice']
            choices = post.getlist('multichoice[]')
        else:
            answers = post.getlist('shortanswer[]')
            correctAnswer = None # want all the answers to go into the problemAnswers table - not into problem.answer
        audioResource = post['audioResource']
        layoutTemplateId = post['layout']
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
            else: insertProblemDifficulty(id,initDifficulty)

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

        return render(request, 'msadmin/qa/qauth_edit.html', {'message': msg, 'errors': errors, 'probId': p.id, 'problem': p, 'hints': hints, 'qaDir': QA_DIR, 'SNAPSHOT_DIRNAME': SNAPSHOT_DIRNAME})

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
def deleteHints (request, probId):
    if request.method == "POST":
        post = request.POST
        # hints are given as an array of ids
        hintIds = post.getlist('data[]')
        for hid in hintIds:
            h = get_object_or_404(Hint,pk=hid)
            h.delete()
            # delete all the rows in the PMF for this hint
            mfs = ProblemMediaFile.objects.filter(problem_id=probId, hint=h)
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





