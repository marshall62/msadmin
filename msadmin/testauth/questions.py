from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
from msadminsite.settings import MEDIA_ROOT
import os
from django.core.files.storage import FileSystemStorage
from .models import *
from msadminsite.settings import SURVEYS_QUEST_DIRNAME

# settings.py has the name of the dir where survey media should be stored.


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
        writeQuestion(q.id,request.POST, request.FILES)
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
    return render(request, 'msadmin/ta/question.html', {'SURVEYS_DIR': SURVEYS_QUEST_DIRNAME + '/'})

def getQuestion (qid):
    q = get_object_or_404(Question,pk=qid)
    return q

def writeQuestion (qid, postData, files):
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
    if 'image' in files:
        imgFile = files['image']
        handle_uploaded_file(qid, imgFile)
        q.imageFilename = imgFile.name
    if 'removeImage' in postData:
        filename = q.imageFilename
        deleteMediaFile(qid,filename)
        q.imageFilename = None
    q.name = name
    q.save()
    return q

def handle_uploaded_file(qid, f):
    # if attempting to upload a file that is already there, it proceeds and overwrites it.
    dirName = Question.DIR_PREFIX + qid
    fullPath = os.path.join(MEDIA_ROOT, SURVEYS_QUEST_DIRNAME,dirName,f.name)
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    with open(fullPath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return True

def deleteMediaFile (qid, fileName):
    # Get the default FileSystemStorage class based on MEDIA_ROOT settings in settings.py
    fs = FileSystemStorage()
    location = fs.location
    base_url = fs.base_url
    file_permissions_mode = fs.file_permissions_mode
    directory_permissions_mode = fs.directory_permissions_mode
    newloc = os.path.join(location, SURVEYS_QUEST_DIRNAME, Question.DIR_PREFIX + qid)
    # Create a new FileSystemStorage object based on the default one.  It uses the new directory for the problem.
    fs2 = FileSystemStorage(location=newloc ,file_permissions_mode=file_permissions_mode,directory_permissions_mode=directory_permissions_mode)
    if fs2.exists(fileName):
        fs2.delete(fileName)



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
        q = writeQuestion(qId,request.POST,request.FILES)
    return q

# URL: GET/POST /pages/questions/<qId>
# process post data and return an HTML view (page) of the question
def gpQuestion_page (request, qId):
    q= gpdQuestion(request, qId)
    message = "Question successfully saved"
    return render(request, 'msadmin/ta/question.html', {'question': q, 'message': message, 'SURVEYS_DIR': SURVEYS_QUEST_DIRNAME+"/"})

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
    models = {'qobj': qobj, 'SURVEYS_DIR': SURVEYS_QUEST_DIRNAME + '/'}
    if testId:
        t = get_object_or_404(Test,pk=testId)
        qs = t.getQuestions()
        # find the next problem after the current one in the test
        nextQ = None
        for i in range(len(qs)):
            if qs[i].id == int(qId):
                nextQ = qs[i+1] if i != len(qs)-1 else None
                break
        if nextQ:
            models['tid'] = testId
            models['qid'] = nextQ.id
        else:
            models['tid'] = testId

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