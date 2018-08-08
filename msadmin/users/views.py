from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import permission_required, user_passes_test
from msadminsite.settings import SESSION_INACTIVITY_TIMEOUT_MIN
from .forms import CustomUserCreationForm, MathspringAdminForm


class MyLoginView (auth_views.LoginView):
    template_name= "registration/login.html"
    name="login"

    # Override the superclass so that we can set a timeout on the session.
    def form_valid(self, form):
        """Security check complete. Log the user in."""
        result = super().form_valid(form)
        self.request.session.set_expiry(60 * SESSION_INACTIVITY_TIMEOUT_MIN)
        return result




# @permission_required('users.can_add_user')
@user_passes_test(lambda u: u.is_staff)
def register(request):
    if request.method == 'POST':
        if 'adminForm' in request.POST:
            g = MathspringAdminForm(request.POST)
            f = None
        else:
            f = CustomUserCreationForm(request.POST)
            g = None

        if f:
            if f.is_valid():
                f.save()
                messages.success(request, 'MSAdmin Account created successfully')
                return redirect('users_main')
            else: g = MathspringAdminForm()

        elif g:
            if g.is_valid():
                g.save()
                messages.success(request, 'Mathspring Teacher Tools Account created successfully')
                return redirect('users_main')
            else: f = CustomUserCreationForm()

    else:
        f = CustomUserCreationForm() # form for MS Admin user
        g = MathspringAdminForm() # form for Mathspring Admin (old teacher tools) user

    return render(request, 'registration/register_author.html', {'form': f, 'form2': g})