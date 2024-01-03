from django.contrib.auth.views import LoginView
from .forms import SignUpForm, SignInForm
from django.urls import reverse_lazy
from django.views import generic


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

class SignInView(LoginView):
    form_class = SignInForm
    success_url = reverse_lazy("index")
    template_name = "registration/signin.html"