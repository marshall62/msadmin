from django.shortcuts import render
from django.http import HttpResponse


def main (request):
    print("here")
    return render(request, 'msadmin/main.html', {})

def signup (request):
    print('signup')
    return HttpResponse("Sign up page")

def login (request):
    print('login')
    return HttpResponse("Login page")