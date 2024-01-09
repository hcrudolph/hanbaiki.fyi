from django.urls import path
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
)
from .views import SignUpView, SignInView, CustomPasswordResetConfirmView
from .forms import PasswordResetForm


urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
    path('password-reset/', PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        email_template_name='accounts/password_reset_email_txt.html',
        html_email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        form_class = PasswordResetForm,
        success_url = reverse_lazy('pw_reset_sent'),
    ), name='password_reset_request'),
    path('password-reset/sent/', PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_sent.html',
    ),name='pw_reset_sent'),
    path('password-reset/confirm/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(),
        name='pw_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ),name='pw_reset_complete'),
]