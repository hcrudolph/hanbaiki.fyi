from django.urls import path
from .views import SignUpView, SignInView

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('login/', SignInView.as_view(), name='login'),
]