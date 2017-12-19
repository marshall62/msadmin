from django.shortcuts import render

from .models import *

def main (request):
    tests = Test.objects.all()
    return render(request, 'msadmin/ta/tests.html', {'tests': tests})

def newTest (request):
    pass

def getTest (request):
    pass

def getTestQuestions (request):
    pass

def addQuestions (request):
    pass

def orderQuestions (request):
    pass

def question (request):
    pass

def tests (request):
    pass

def test (request):
    pass

def previewQuestion (request):
    pass