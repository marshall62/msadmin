import os

from django.core.files.storage import FileSystemStorage
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404

from msadmin.qa.util import handle_uploaded_file, deleteProblemAnswers, saveProblemMultiChoices, \
    saveProblemShortAnswers, getProblemDirName
from msadminsite.settings import MEDIA_URL
from .qauth_model import *


# CONTENT_MEDIA_URL = "http://rose.cs.umass.edu/mathspring/mscontent/html5Probs/"

# Shows the main page of the site
def main (request):
    probs = Problem.get_quickAuth_problems()
    return render(request, 'msadmin/qa/qauth_main.html', {'problems': probs})

# Produces a page that has react js but the bootstrap styling doesn't work
def reactTest(request):
    prob = get_object_or_404(Problem, pk=1338)
    return render(request, 'msadmin/react1.html', {'problem': prob})

# support for AJAX call from a checkbox next to a intervention-selector node in the jstree
# It will set the isActive field in the class_sc_is_map table to true or false.
def create_problem (request):
    return render(request, 'msadmin/qa/qauth_edit.html', {'probId': -1})

def edit_problem (request, probId):
    prob = get_object_or_404(Problem, pk=probId)
    hints = Hint.objects.filter(problem=prob).order_by('order')
    return render(request, 'msadmin/qa/qauth_edit.html', {'probId': probId, 'problem': prob, 'hints': hints, 'mediaURL': MEDIA_URL})

# write the file to path/problem_probId/f.name
# no longer used.  We use the handle_uploaded_file above instead
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
        standardId = post['standardId']
        clusterId = post['clusterId']
        questType = post['questType']
        correctAnswer=None
        if questType == Problem.MULTI_CHOICE:
            correctAnswer = post['correctChoice']
            choices = post.getlist('multichoice[]')
        else:
            answers = post.getlist('shortanswer[]')
            correctAnswer = None # want all the answers to go into the problemAnswers table - not into problem.answer
        audioResource = post['audioResource']
        layoutId = post['layout']
        audioResource = 'question' if audioResource == 'hasAudio' else None
        form= 'quickAuth'
        if 'imageFile' in request.FILES:
            imgFile = request.FILES['imageFile']
            imageURL = None

        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            audioResource= audFile.name.split('.')[0] # get rid of the file extension e.g.


        if not id:
            p = Problem(name=name,nickname=nickname,statementHTML=statementHTML,answer=correctAnswer,
                        imageURL=imageURL,status=status,standardId=standardId,clusterId=clusterId,form=form,
                        questType=questType, audioResource=audioResource, layout_id=layoutId)


        else:
            p = get_object_or_404(Problem, pk=id)
            p.setFields(name=name,nickname=nickname,statementHTML=statementHTML,answer=correctAnswer,
                        status=status,standardId=standardId,clusterId=clusterId,form=form,
                        questType=questType, layout_id=layoutId)
            # if no audio or image file are given we don't want to overwrite the problem's audio or image with NULL
            # because it may have these files and we don't want problem-save eliminating them
            if imageURL:
                p.imageURL=imageURL
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
    return redirect("qauth_edit_prob",probId=probId)




def deleteHints (request, probId):
    if request.method == "POST":
        post = request.POST
        # hints are given as an array of ids
        hintIds = post.getlist('data[]')
        for hid in hintIds:
            h = get_object_or_404(Hint,pk=hid)
            h.delete()
        # after deleting there may be holes in the ordering sequence, so we renumber all the remaining hints
        # 1-based ordering is used
        hints = Hint.objects.filter(problem_id=probId).order_by('order')
        for i in range(len(hints)):
            hints[i].order = i+1
            if not hints[i].givesAnswer:
                hints[i].name = 'Hint ' + str(i+1);
            hints[i].save()
    return redirect("qauth_edit_prob",probId=probId)


