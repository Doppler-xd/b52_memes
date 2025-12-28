from django import forms
from .models import Meme, TextBlock


class MemeForm(forms.ModelForm):
    class Meta:
        model = Meme
        fields = ['name', 'template', 'custom_image', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'template': forms.Select(attrs={'class': 'form-control'}),
            'custom_image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class TextBlockForm(forms.ModelForm):
    class Meta:
        model = TextBlock
        fields = ['text', 'font_size', 'font_family', 'color', 'stroke_color',
                 'position_type', 'position_area', 'x', 'y']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'font_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'font_family': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'stroke_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'position_type': forms.Select(attrs={'class': 'form-control'}),
            'position_area': forms.Select(attrs={'class': 'form-control'}),
            'x': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'y': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }