from django.contrib.auth import get_user_model
from captcha.fields import CaptchaField, CaptchaTextInput
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)

User = get_user_model()

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'username']
        help_texts = {'email': 'Required. Only used for letting you reset your password.',}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'off',
            'type': 'email',
            'id': 'EmailInput',
        })
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'autocomplete': 'off',
            'id': 'UsernameInput',
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'id': 'Password1Input',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'id': 'Password2Input',
        })

    captcha = CaptchaField(
        widget=CaptchaTextInput(attrs={
            'class': 'form-control',
            'id': 'CaptchaInput',
        })
    )

class SignInForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'id': 'UsernameInput',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'type': 'password',
            'id': 'PasswordInput',
        })

    captcha = CaptchaField(
        widget=CaptchaTextInput(attrs={
            'class': 'form-control',
            'id': 'CaptchaInput',
        })
    )

class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'id': 'EmailInput'
        })

class PasswordResetConfirmForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'id': 'Password1Input',
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'id': 'Password2Input',
        })