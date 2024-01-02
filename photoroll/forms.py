from django.forms import ModelForm
from .models import VendingMachine
from django.contrib.auth import get_user_model

User = get_user_model()

class UploadForm(ModelForm):
    class Meta:
        model = VendingMachine
        fields = ["img"]
        labels = {
            "img": "",
        }


class SignUpForm(ModelForm):
    class Meta:
        model = User
        fields = ["email", "username", "password"]