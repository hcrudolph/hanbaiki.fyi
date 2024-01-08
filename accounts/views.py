from django.contrib.auth.views import LoginView, PasswordResetConfirmView
from .forms import SignUpForm, SignInForm, PasswordResetConfirmForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

class SignInView(LoginView):
    form_class = SignInForm
    success_url = reverse_lazy('index')
    template_name = 'accounts/signin.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = PasswordResetConfirmForm
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully.')
        return super().form_valid(form)
