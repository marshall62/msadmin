from django.shortcuts import render
import django

def login (request):
    print(django.VERSION)
    if request.method == 'GET':
        return render(request, 'registration/login.html')
    elif request.method == 'POST':
        post = request.POST
        # uname = post['user']