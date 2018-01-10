from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse

from .models import *


def main (request):
    pass

# URL: GET/POST /pages/questions
# GET (all) returns a page showing all questions
# POST data contains a new question which is saved and then returned as a page view of that question
def all_page (request):
    if request.method == "GET":
        qs = Question.objects.all()
        return render(request,'msadmin/ta/questions.html',{'questions': qs})
    elif request.method == "POST":
        testId = request.POST['testId'] # may be present if saving a new question within a test
        q = Question(ansType=0)
        q.save()
        # Put the question in the test if testId is present
        if testId:
            t = get_object_or_404(Test,pk=testId)
            t.addQuestion(q)
        writeQuestion(q.id,request.POST)
        return redirect("ta_questions_gp_page",qId=q.id)





def deleteQuestions_page (request):
    if request.method == "POST":
        payload = request.POST
        qids = payload.getlist('removeQuestion[]')
        for qid in qids:
            q = get_object_or_404(Question,pk=qid)
            q.delete()
    return redirect('ta_questions_all_page')

# URL: GET /questions
# return JSON that is all the questions
def all_json (request):
    if request.method == "GET":
        qs = Question.objects.all()
        return JsonResponse(questions_json(qs),safe=False)

# URL GET pages/questions/new
# return a page that shows an empty question form
def newQuestion_page (request):
    return render(request, 'msadmin/ta/question.html', {})

def getQuestion (qid):
    q = get_object_or_404(Question,pk=qid)
    return q

def writeQuestion (qid, postData):
    q = get_object_or_404(Question,pk=qid)

    name = postData['name']
    type = postData['type']
    hoverText = postData['hoverText']
    answer = postData['answer']
    description = postData['description']
    warnTime = postData['warnTime']
    aAns = postData['aAns']
    bAns = postData['bAns']
    cAns = postData['cAns']
    dAns = postData['dAns']
    eAns = postData['eAns']
    correctChoice = postData['multiChoiceCorrectAnswer']
    q.name=name
    if type == 'multiChoice':
        q.ansType = Question.MULTI_CHOICE
    elif type == 'shortAnswer':
        q.ansType = Question.SHORT_ANSWER
    else:
        q.ansType = Question.LONG_ANSWER
    q.hoverText=hoverText
    q.description=description
    if warnTime == 'unlimited':
        q.waitTimeSecs = Question.UNLIMITED
    else: q.waitTimeSecs=warnTime
    q.aChoice=aAns
    q.bChoice=bAns
    q.cChoice=cAns
    q.dChoice=dAns
    q.eChoice=eAns
    if type=="multiChoice" and correctChoice != 'noneCorrect':
        q.answer=correctChoice
    elif type=="multiChoice" and correctChoice == 'noneCorrect':
        q.answer=None
    else:
        q.answer=answer
    # TODO add image upload into blob
    # image = postData['image']
    if 'removeImage' in postData:
        q.image = None
    q.name = name
    q.save()
    return q

def deleteQuestion (qid):
    q = get_object_or_404(Question,pk=qid)
    q.delete()

# handle the GET/POST/DEL operations on questions.
def gpdQuestion (request, qId):
    if request.method == "GET":
        q = getQuestion(qId)
    elif request.method == "DELETE":
        deleteQuestion(qId)
    elif request.method == "POST":
        q = writeQuestion(qId,request.POST)
    return q

# URL: GET/POST /pages/questions/<qId>
# process post data and return an HTML view (page) of the question
def gpQuestion_page (request, qId):
    q= gpdQuestion(request, qId)
    message = "Question successfully saved"
    return render(request, 'msadmin/ta/question.html', {'question': q, 'message': message})

# GIven a list of question objects, return JSON that is a list of their ids and a list of the objects.
def questions_json (questions):
    if len(questions) > 0:
        objs = [q.toJSON() for q in questions]
        ids = [q.id for q in questions]
        return {'qids': ids, 'questions': objs}
    else: return {}

# URL GET /pages/tests/<testId>/questions/<qId>/preview
# URL GET /pages/questions/<qId>/preview
# Return a page that previews a question.  If test is given, find the next question in the test and pass its id to the template
# so that a "next question" button can be placed in the page.
def questionPreview_page (request, qId, testId=None):
    qobj = getQuestion(qId)
    if not testId:
        models = {'qobj': qobj}
    else:
        t = get_object_or_404(Test,pk=testId)
        qs = t.getQuestions()
        # find the next problem after the current one in the test
        nextQ = None
        for i in range(len(qs)):
            if qs[i].id == int(qId):
                nextQ = qs[i+1] if i != len(qs)-1 else None
                break
        if nextQ:
            models = {'qobj': qobj, 'tid': testId, 'qid': nextQ.id }
        else: models = {'qobj': qobj, 'tid': testId }


    return render(request,'msadmin/ta/questionPreview.html', models)

# URL: GET /questions/<qId>/image
# return the stream of binary info from the image blob in the question.  This will
# placed in an <img src="xxx"> tag.
def getQuestionImage (request, qId):
    pass


def getQuestionDescription (request):
    pass

def previewQuestion (request):
    pass

def newQuestion (request):
    pass