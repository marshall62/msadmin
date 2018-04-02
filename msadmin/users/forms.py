from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Administrator
from django import forms
from django.core.exceptions import ValidationError


class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Enter Username', min_length=4, max_length=150)
    email = forms.EmailField(label='Enter email')
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user


class MathspringAdminForm (CustomUserCreationForm):

    def clean_username(self):
        validated = self.cleaned_data['username']
        if validated:
            try:
                a = Administrator.objects.get(userName=validated)
            except Administrator.DoesNotExist:
                a = None
            if a:
                raise ValidationError("Username already exists!")
            else: return validated


    def pwHash (self, pw):
        hpw = "";
        x = 13;
        for i in range(len(pw)):
            num = (ord(pw[i]) * i+1 * x) % (ord("z") - ord("A"))
            c = chr(ord("A") + num);
            hpw += c;
        return hpw

    def clean_password2(self):
        validated = super().clean_password2()
        if validated:
            password2 = self.pwHash(validated)
            return password2
        else:
            raise ValidationError("Problem with pw2")

    def save(self):
        admin = Administrator(userName=self.cleaned_data['username'],
                              email=self.cleaned_data['email'],
                              pw2=self.cleaned_data['password2'])
        admin.save()
        return admin