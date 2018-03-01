from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import permission_required
from msadminsite.settings import SESSION_INACTIVITY_TIMEOUT_MIN
from .forms import CustomUserCreationForm


class MyLoginView (auth_views.LoginView):
    template_name= "registration/login.html"
    name="login"

    # Override the superclass so that we can set a timeout on the session.
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        result = super().form_valid(form)
        self.request.session.set_expiry(60 * SESSION_INACTIVITY_TIMEOUT_MIN)
        return result




@permission_required('users.can_add_user')
def register(request):
    if request.method == 'POST':
        f = CustomUserCreationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(request, 'Account created successfully')
            return redirect('users_main')

    else:
        f = CustomUserCreationForm()

    return render(request, 'registration/register_author.html', {'form': f})