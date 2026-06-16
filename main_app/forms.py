import re

from django import forms

from .models import Client

HEX_COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')
INPUT_CLASS = 'form-input'


class TenantBrandingForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['display_name', 'tagline', 'logo', 'primary_color', 'sidebar_color']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Your company name'}),
            'tagline': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Courier & Cargo Management'}),
            'logo': forms.FileInput(attrs={'class': 'form-input'}),
            'primary_color': forms.TextInput(attrs={'class': INPUT_CLASS, 'type': 'color'}),
            'sidebar_color': forms.TextInput(attrs={'class': INPUT_CLASS, 'type': 'color'}),
        }

    def clean_primary_color(self):
        value = self.cleaned_data['primary_color']
        if value and not HEX_COLOR_RE.match(value):
            raise forms.ValidationError('Enter a valid hex color, e.g. #3b82f6')
        return value

    def clean_sidebar_color(self):
        value = self.cleaned_data['sidebar_color']
        if value and not HEX_COLOR_RE.match(value):
            raise forms.ValidationError('Enter a valid hex color, e.g. #1e2a4a')
        return value
