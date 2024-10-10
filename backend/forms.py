from django import forms
from .models import BaseTemplate

class BaseTemplateForm(forms.ModelForm):
    class Meta:
        model = BaseTemplate
        fields = ['file']

class JobDescriptionForm(forms.Form):
    job_description = forms.CharField(widget=forms.Textarea)