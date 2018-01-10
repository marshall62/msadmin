from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from .models import *
from .questions import questions_json


def main (request):
    return redirect('ta_tests_all_page')

# URL: GET/POST /pages/tests
# GET: will return a page that lists all tests
# POST: will create a new test and will redirect to a page view of that new (empty) test
def all_page (request):
    if request.method == "GET":
        tests = Test.objects.all()
        return render(request, 'msadmin/ta/tests.html', {'tests': tests})
    # post will include all the fields that define the test, but here we just create the new Test object
    # and then forward to getPostTest to complete the task of building it and returning the view of it
    elif request.method == "POST":
        test = Test(isActive=False)
        test.save()
        writeTest(test.id,request.POST)
        return redirect('ta_tests_gp_page',testId=test.id)

# URL: GET /pages/tests/new
# requests a page for entering a new test's info
def newTest_page (request):
    # the test.html page must handle null inputs and create a blank form.
    return render(request, 'msadmin/ta/test.html', {})

def getTest (testId):
    t = get_object_or_404(Test, pk=testId)
    return t

def deleteTest (testId):
    t = get_object_or_404(Test, pk=testId)
    t.delete()

def writeTest (testId, postData):
    name = postData['name']
    t = get_object_or_404(Test, pk=testId)
    t.name = name
    if 'isActive' in postData:
        t.isActive = True
    else: t.isActive = False
    t.save()
    return t

# perform the various GET/POST/DELETE operations for a given testId and post inputs
def gpdTest (request, testId):
    if request.method == "GET":
        t = getTest(testId)
    elif request.method == "POST":
        t = writeTest(testId, request.POST)
    elif request.method == "DELETE":
        deleteTest(testId)
    return t

# URL: DELETE /pages/tests/remove
# post has a payload of test ids to remove.  The tests are deleted. We return a page of all remaining tests
def deleteTests_page (request):
    if request.method == "POST":
        post = request.POST
        ids = post.getlist('removeTest[]')
        for id in ids:
            deleteTest(id)
    return redirect('ta_tests_all_page')

# URL: GET/POST /pages/tests/<testID>
# return a page view of the test in question and process post data to write the test.
def gpTest_page (request, testId):
    t = gpdTest(request,testId)
    qs = t.getQuestions()
    return render(request, 'msadmin/ta/test.html', {'test': t, 'questions': qs, 'message': None})

# URL: GET /pages/tests/<testId>/questions/new
# redirects to the question editor page with no question and the given test.
def newTestQuestion_page (request, testId):
    return render(request, 'msadmin/ta/question.html', {'testId':testId})

# URL: DELETE /tests/<testId>/questions/<qId>
#  remove the question from the test.  Return json which is the list of questions remaining in the test
def deleteTestQuestions_json (request, testId, qId):
    if request.method == "DELETE":
        # TODO HOW is this working??? Filter returns multiple items and might need the table to have ID
        print("deleteTestQuestions might be failing to delete the question")
        m = TestQuestionMap.objects.filter(test_id=testId, question_id=qId)
        m.delete()
        # now that the t->q map row is removed, get the test (hopefully it won't have this question in it)
        return JsonResponse(getTestQuestion_json(testId),safe=False)

# URL: POST /tests/<testId>/questions
#  The post payload is a list of question ids to add to this test.
# Returns the questions in the test as json
def addTestQuestions_json (request, testId):
    if request.method == "POST":
        post = request.POST
        qids = post.getlist('ids[]')
        t = getTest(testId)
        qs = t.getQuestions()
        pos = len(qs) # positions are 0 based in db so position of new ones starts at cur length
        for id in qids:
            m = TestQuestionMap(test_id=testId,question_id=id,position=pos)
            m.save()
            pos += 1
        # now that the t->q map row increased, get the test questions(hopefully it won't have this question in it)
        return JsonResponse(getTestQuestion_json(testId),safe=False)

#URL: GET /tests/questions
# Returns a JSON list of questions in the test
def testQuestions_json (request, testId):
    if request.method == "GET":
        return JsonResponse(getTestQuestion_json(testId),safe=False)

# Return json like {qids: [1,2,3,], questions: [{id: 1, name='a'}, {id...}]}
def getTestQuestion_json (testId):
    t = getTest(testId)
    # qs = t.questions.all().order_by('position');
    # TODO this needs to return a list of questions in order of position.
    qs = t.getQuestions()

    return questions_json(qs)

# URL GET /pages/tests/<testId>/preview
# redirects to test question previewer for the first question in the test
def testPreview_page (request, testId):
    t = getTest(testId)
    q = t.getQuestions().first()
    return redirect('ta_tests_question_preview_page', testId=testId, qId=q.id)

def setIds ():
    ms = TestQuestionMap.objects.all()
    i = 1
    for m in ms:
        m.id = i
        m.save()
        i += 1



# URL: POST /tests/<testId>/questions/order
# save a new ordering of the tests questions
def testQuestionsOrder_json (request, testId):
    if request.method == 'POST':
        post = request.POST
        ids = post.getlist('ids[]') # the question Ids in the new order
        pos = 0
       # setIds()
        for qid in ids:
            ms = TestQuestionMap.objects.filter(question_id=qid, test_id=testId)
            c = ms.count()
            m = ms.first()
            m.position = pos
            m.save()
            pos += 1

    return JsonResponse({})

def testQuestions (request, testId):
    pass

# As a GET request it will return a page for entering the question info
def addQuestions (request, testId):
    pass

def orderQuestions (request):
    pass

def question (request):
    pass



def test (request):
    pass

def previewQuestion (request):
    pass

def previewTest (request):
    pass