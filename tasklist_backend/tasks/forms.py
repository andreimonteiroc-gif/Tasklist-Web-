"""
Formulários para autenticação, registro e gerenciamento de tarefas.
"""
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Task, UserProfile


class LoginForm(forms.Form):
    """Formulário de login."""
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )
    remember_me = forms.BooleanField(
        label='Lembrar-me',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class RegisterForm(forms.Form):
    """Formulário de registro de novo usuário."""
    
    name = forms.CharField(
        label='Nome Completo',
        min_length=2,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome completo'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com'
        })
    )
    password = forms.CharField(
        label='Senha',
        min_length=6,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 6 caracteres'
        })
    )
    password_confirm = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
    )
    
    def clean(self):
        """Valida se as senhas coincidem."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError('As senhas não coincidem.')
        
        return cleaned_data
    
    def clean_email(self):
        """Valida se email já está registrado."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este email já está cadastrado.')
        return email


class TaskForm(forms.ModelForm):
    """Formulário para criação e edição de tarefas."""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o título da tarefa'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descrição da tarefa (opcional)',
                'rows': 4
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'title': 'Título',
            'description': 'Descrição',
            'priority': 'Prioridade',
        }
    
    def clean_title(self):
        """Valida título da tarefa."""
        title = self.cleaned_data.get('title')
        if title and len(title.strip()) < 3:
            raise ValidationError('Título deve ter pelo menos 3 caracteres.')
        return title.strip() if title else title


class UserProfileForm(forms.ModelForm):
    """Formulário para edição de perfil de usuário."""
    
    first_name = forms.CharField(
        label='Primeiro Nome',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = ['full_name']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo'
            }),
        }
        labels = {
            'full_name': 'Nome Completo',
        }
    
    def clean_full_name(self):
        """Valida nome completo."""
        full_name = self.cleaned_data.get('full_name')
        if full_name and len(full_name.strip()) < 2:
            raise ValidationError('Nome deve ter pelo menos 2 caracteres.')
        return full_name.strip() if full_name else full_name
