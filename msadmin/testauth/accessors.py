from django.shortcuts import get_object_or_404
from .models import Test


def fetchTest (testId):
    t = get_object_or_404(Test, pk=testId)
    return t