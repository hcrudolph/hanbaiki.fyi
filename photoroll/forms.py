from django import forms
from .models import VendingMachine

class UploadForm(forms.ModelForm):
    class Meta:
        model = VendingMachine
        fields = ["img"]
        labels = {
            "img": "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['img'].widget.attrs.update({
            'class': 'form-control',
            'type': 'file',
            'id': 'ImgInput',
            'multiple': 'True',
        })

    widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'CaptchaInput'
    })
