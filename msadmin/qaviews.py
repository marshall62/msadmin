from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, render_to_response
from django.shortcuts import redirect
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
        audioResource = 'question' if audioResource == 'hasAudio' else None
        form= 'quickAuth'
        if not id:
            p = Problem(name=name,nickname=nickname,statementHTML=statementHTML,answer=answer,
                    imageURL=imageURL,status=status,standardId=standardId,clusterId=clusterId,form=form,
                    questType=questType, audioResource=audioResource)
        else:
            p = get_object_or_404(Problem, pk=id)
            p.setFields(name=name,nickname=nickname,statementHTML=statementHTML,answer=answer,
                        imageURL=imageURL,status=status,standardId=standardId,clusterId=clusterId,form=form,
                        questType=questType, audioResource=audioResource)
        p.save()
        probId = p.pk
    return redirect("qauth_edit_prob",probId=probId)

