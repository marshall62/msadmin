from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.shortcuts import redirect
from django.core.files.storage import FileSystemStorage
import os
import sys
from .submodel.qauth_model import *

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
    return render(request, 'msadmin/qauth_edit.html', {'probId': probId, 'problem': prob, 'hints': hints})

def save_problem (request):
    if request.method == "POST":
        post = request.POST
        id = post['id']
        name = post['name']
        nickname = post['nickname']
        statementHTML = post['statementHTML']
        answer = post['answer']
        imageURL = post['imageURL']
        status = post['status']
        standardId = post['standardId']
        clusterId = post['clusterId']
        questType = post['questType']
        audioResource = post['audioResource']
        layoutId = post['layout']
        audioResource = 'question' if audioResource == 'hasAudio' else None
        form= 'quickAuth'
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
        if 'imageFile' in request.FILES:
            imgFile = request.FILES['imageFile']
            imageURL = '{[' + imgFile.name + ']}' # change the imageURL saved in the db to the name of this file.
            if fs2.exists(imgFile.name):
                fs2.delete(imgFile.name)
            fs2.save(imgFile.name, imgFile)

        if 'audioFile' in request.FILES:
            audFile = request.FILES['audioFile']
            if fs2.exists(audFile.name):
                fs2.delete(audFile.name)
            fs2.save(audFile.name, audFile)

        if not id:
            p = Problem(name=name,nickname=nickname,statementHTML=statementHTML,answer=answer,
                    imageURL=imageURL,status=status,standardId=standardId,clusterId=clusterId,form=form,
                    questType=questType, audioResource=audioResource, layout_id=layoutId)
        else:
            p = get_object_or_404(Problem, pk=id)
            p.setFields(name=name,nickname=nickname,statementHTML=statementHTML,answer=answer,
                        imageURL=imageURL,status=status,standardId=standardId,clusterId=clusterId,form=form,
                        questType=questType, audioResource=audioResource,layout_id=layoutId)
        p.save()
        probId = p.pk
    return redirect("qauth_edit_prob",probId=probId)

def getHint (request, hintId):
    h = get_object_or_404(Hint,pk=hintId)
    d = {}
    d['id'] = hintId
    d['name'] = h.name
    d['statementHTML'] = h.statementHTML
    d['audioResource'] = h.audioResource
    d['order'] = h.order
    d['hoverText'] = h.hoverText
    d['givesAnswer'] = h.givesAnswer
    return JsonResponse(d)

def saveHint (request, probId):
    if request.method == "POST":
        post = request.POST
        id = post['id']
        name = post['name']
        statementHTML = post['statementHTML']
        hoverText = post['hoverText']
        audioResource = post['audioResource']
        order = post['order']
        givesAnswer = post['givesAnswer']
        if id:
            h = get_object_or_404(Hint,pk=id)
            h.name=name
            h.statementHTML=statementHTML
            h.audioResource=audioResource
            h.hoverText=hoverText
            h.order=order
            h.givesAnswer=givesAnswer=='true'
            h.save()
        else:
            hints = Hint.objects.filter(problem_id=probId)
            order = len(hints) + 1
            h = Hint(name=name,statementHTML=statementHTML,problem_id=probId,audioResource=audioResource,hoverText=hoverText,order=order,givesAnswer=givesAnswer=='true')
            h.save()
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
            hints[i].save()
    return redirect("qauth_edit_prob",probId=probId)

def getLayouts (request):
    layouts = ProblemLayout.objects.all()
    # create a list of layout objects in json
    a = [l.toJSON() for l in layouts]
    return JsonResponse(a,safe=False)