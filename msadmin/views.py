from django.shortcuts import render
from django.http import HttpResponse


def main (request):
    print("here")
    return render(request, 'msadmin/main.html', {})

def util (request):
    return render(request, 'msadmin/util.html', {})

