from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from msadminsite.settings import SESSION_INACTIVITY_TIMEOUT_MIN
import django


class UserCreateForm(UserCreationForm):
    username = forms.CharField(required = True, max_length = 30)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required = False, max_length = 30)
    last_name = forms.CharField(required = False, max_length = 30)

    # class Meta:
    #     model = User
    #     fields = ("username", "email", "password1", "password2")

    def clean(self, *args, **kwargs):
        """
        Normal cleanup + username generation.
        """
        cleaned_data = super(UserCreationForm, self).clean(*args, **kwargs)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit)
        user.email = self.cleaned_data["email"]
        # user.first_name = self.cleaned_data['first_name']
        # user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

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

