from django.contrib.auth import get_user_model
from captcha.fields import CaptchaField, CaptchaTextInput
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["email", "username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'type': 'email',
            'id': 'EmailInput'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'id': 'UsernameInput'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'id': 'Password1Input'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'id': 'Password2Input'
        })

    captcha = CaptchaField(
        widget=CaptchaTextInput(attrs={
            'class': 'form-control',
            'id': 'CaptchaInput'
        })
    )

class SignInForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'id': 'UsernameInput'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'id': 'PasswordInput'
        })

    captcha = CaptchaField(
        widget=CaptchaTextInput(attrs={
            'class': 'form-control',
            'id': 'CaptchaInput'
        })
    )