from django.shortcuts import render

def login (request):
    if request.method == 'GET':
        return render(request, 'registration/login.html')
    elif request.method == 'POST':
        post = request.POST
        # uname = post['user']