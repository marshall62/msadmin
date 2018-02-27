from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from msadminsite.settings import SESSION_INACTIVITY_TIMEOUT_MIN
import django

class MyLoginView (auth_views.LoginView):
    template_name= "registration/login.html"
    name="login"

    # Override the superclass so that we can set a timeout on the session.
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        result = super().form_valid(form)
        self.request.session.set_expiry(60 * SESSION_INACTIVITY_TIMEOUT_MIN)
        return result

######## Unused stuff below


def doLogin (request):
    if request.method == 'GET':
        return render(request, 'registration/login_old.html')
    elif request.method == 'POST':
        post = request.POST
        print(django.VERSION)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('msadmin_main')
        else:
            return render(request, 'registration/login_old.html', {'message': "Login failed: User or password is incorrect"})


def doLogout (request):
    logout(request)
    return render(request, 'registration/logo.html')

def doPWReset (request) :
    pass

