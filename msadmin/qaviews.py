from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
import os
import sys
from .submodel.qauth_model import *

CONTENT_MEDIA_URL = "http://rose.cs.umass.edu/mathspring/mscontent/html5Probs/"

# Shows the main page of the site
def main (request):
    probs = Problem.get_quickAuth_problems()
    return render(request,'msadmin/qauth_main.html', {'problems': probs})

# Produces a page that has react js but the bootstrap styling doesn't work
def reactTest(request):
    prob = get_object_or_404(Problem, pk=1338)
    return render(request, 'msadmin/react1.html', {'problem': prob})

# support for AJAX call from a checkbox next to a intervention-selector node in the jstree
# It will set the isActive field in the class_sc_is_map table to true or false.
def create_problem (request):
    return render(request, 'msadmin/qauth_edit.html', {'probId': -1})

def edit_problem (request, probId):
    prob = get_object_or_404(Problem, pk=probId)
    hints = Hint.objects.filter(problem=prob).order_by('order')
    return render(request, 'msadmin/qauth_edit.html', {'probId': probId, 'problem': prob, 'hints': hints, 'mediaURL': CONTENT_MEDIA_URL})

def saveMedia (name, file):
    # Get the default FileSystemStorage class based on MEDIA_ROOT settings in settings.py
    fs = FileSystemStorage()
    location = fs.location
    base_url = fs.base_url
    file_permissions_mode = fs.file_permissions_mode
    directory_permissions_mode = fs.directory_permissions_mode
    newPath = os.path.join(location, name)
    # MEDIA_ROOT (on the server) is the location of the mscontent/html5Problems directory within the Apache
    # server.   This creates a directory in there with the name of the problem (or proceeds if it exists).
    try:
        os.mkdir(newPath)
    except FileExistsError as e:
        pass

    newloc = os.path.join(location, name)
    # Create a new FileSystemStorage object based on the default one.  It uses the new directory for the problem.
    fs2 = FileSystemStorage(location=newloc ,base_url=base_url,file_permissions_mode=file_permissions_mode,directory_permissions_mode=directory_permissions_mode)
    if fs2.exists(file.name):
        fs2.delete(file.name)
    fs2.save(file.name, file)


def deleteMediaFile (fileName):
    # Get the default FileSystemStorage class based on MEDIA_ROOT settings in settings.py
    fs = FileSystemStorage()
    location = fs.location
    base_url = fs.base_url
    file_permissions_mode = fs.file_permissions_mode
    directory_permissions_mode = fs.directory_permissions_mode
    newPath = os.path.join(location, fileName)
    newloc = os.path.join(location, fileName)
    # Create a new FileSystemStorage object based on the default one.  It uses the new directory for the problem.
    fs2 = FileSystemStorage(location=newloc ,base_url=base_url,file_permissions_mode=file_permissions_mode,directory_permissions_mode=directory_permissions_mode)
    if fs2.exists(fileName):
        fs2.delete(fileName)

def save_problem_media (request, probId):
    if request.method == "POST":
        post = request.POST

        if 'mediaFiles[]' in request.FILES:
            #files = post.getlist('mediaFiles[]')
            p = get_object_or_404(Problem,pk=probId)
            files = request.FILES.getlist('mediaFiles[]')
            for f in files:
                pmf = ProblemMediaFile(filename=f.name,problem=p)
                pmf.save()
                saveMedia(f.name,f)
    return redirect("qauth_edit_prob",probId=probId)

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
            saveMedia(imgFile.name,imgFile)
            imageURL = '{[' + imgFile.name + ']}' # change the imageURL saved in the db to the name of this file.


        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            saveMedia(audFile.name,audFile)
            audioResource= audFile.name.split('.')[0] # get rid of the file extension e.g.

        if not id:
            p = Problem(name=name,nickname=nickname,statementHTML=statementHTML,answer=correctAnswer,
                    imageURL=imageURL,status=status,standardId=standardId,clusterId=clusterId,form=form,
                    questType=questType, audioResource=audioResource, layout_id=layoutId)

        else:
            p = get_object_or_404(Problem, pk=id)
            p.setFields(name=name,nickname=nickname,statementHTML=statementHTML,answer=correctAnswer,
                        imageURL=imageURL,status=status,standardId=standardId,clusterId=clusterId,form=form,
                        questType=questType, audioResource=audioResource,layout_id=layoutId)
        p.save()
        probId = p.pk
        # if its a multichoice problem delete all the problem answers and add the given list
        if questType==Problem.MULTI_CHOICE:
            deleteProblemAnswers(p)
            saveProblemMultiChoices(p,correctAnswer,choices)
        else:
            deleteProblemAnswers(p)
            saveProblemShortAnswers(p,correctAnswer,answers)
    return redirect("qauth_edit_prob",probId=probId)

def deleteProblemAnswers (problem):
    answers = problem.getAnswers()
    for a in answers:
        a.delete()

def saveProblemMultiChoices (problem, correctAnswer, choices):
    i=0
    for c,l in zip(choices,['a','b','c','d','e']):
        pa = ProblemAnswer(choiceLetter=l,val=c,order=i,problem=problem)
        pa.save()
        i += 1

def saveProblemShortAnswers (problem, correctAnswer, answers):
    i=0
    for a in answers:
        pa = ProblemAnswer(val=a,order=i,problem=problem)
        pa.save()
        i += 1

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

def saveHint (request, probId):
    if request.method == "POST":
        post = request.POST
        id = post['id']
        statementHTML = post['statementHTML']
        hoverText = post['hoverText']
        imageURL = post['imageURL']
        audioResource = post['audioResource']
        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            audioResource = audFile.name
            saveMedia(audFile.name,audFile)

        if 'imageFile' in request.FILES:
            imgFile = request.FILES['imageFile']
            imageURL = imgFile.name
            saveMedia(imgFile.name,imgFile)
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
            h.givesAnswer=givesAnswer
            h.save()
        else:
            hints = Hint.objects.filter(problem_id=probId)
            name = 'Hint ' + str(len(hints) + 1)
            order = len(hints)
            # Hint names are like Hint 1, Hint 2 ... the order field is 0-based
            h = Hint(name=name,statementHTML=statementHTML,problem_id=probId,audioResource=audioResource,imageURL=imageURL,hoverText=hoverText,order=order,givesAnswer=givesAnswer)
            h.save()

    json = h.toJSON()
    return JsonResponse(json)
    # return redirect("qauth_edit_prob",probId=probId)

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


def deleteMedia (request, probId):
    if request.method == "POST":
        post = request.POST
        # hints are given as an array of ids
        mediaIds = post.getlist('data[]')
        for mid in mediaIds:
            mf = get_object_or_404(ProblemMediaFile,pk=mid)
            deleteMediaFile(mf.filename)
            mf.delete()
    return redirect("qauth_edit_prob",probId=probId)

def getLayouts (request):
    layouts = ProblemLayout.objects.all()
    # create a list of layout objects in json
    a = [l.toJSON() for l in layouts]
    return JsonResponse(a,safe=False)

def getProblemJSON (request, probId):
    p = get_object_or_404(Problem,pk=probId)
    js = p.toJSON()
    return JsonResponse(js,safe=False)