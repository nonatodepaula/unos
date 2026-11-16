from django import forms
from .models import Evento, Participante

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Rancho Semanal / Café da Equipe'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = ['usuario', 'modalidade', 'contrib_rancho', 'contrib_cafe', 'contrib_extra']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select'}),
            'modalidade': forms.Select(attrs={'class': 'form-select', 'id': 'id_modalidade'}),
            'contrib_rancho': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_contrib_rancho'}),
            'contrib_cafe': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_contrib_cafe'}),
            'contrib_extra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_contrib_extra'}),
        }

class EditarParticipanteForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = ['modalidade', 'contrib_rancho', 'contrib_cafe', 'contrib_extra']
        widgets = {
            'modalidade': forms.Select(attrs={'class': 'form-select', 'id': 'id_modalidade'}),
            'contrib_rancho': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_contrib_rancho'}),
            'contrib_cafe': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_contrib_cafe'}),
            'contrib_extra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_contrib_extra'}),
        }

class MinhaParticipacaoForm(forms.ModelForm):
    class Meta:
        model = Participante
        fields = ['modalidade', 'contrib_rancho', 'contrib_cafe', 'contrib_extra']
        widgets = {
            'modalidade': forms.Select(attrs={'class': 'form-select', 'id': 'id_minha_modalidade'}),
            'contrib_rancho': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_minha_contrib_rancho'}),
            'contrib_cafe': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_minha_contrib_cafe'}),
            'contrib_extra': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_minha_contrib_extra'}),
        }
