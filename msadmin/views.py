from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def main (request):
    print("here")
    return render(request, 'msadmin/main.html', {})

@login_required
def util (request):
    return render(request, 'msadmin/util.html', {})

