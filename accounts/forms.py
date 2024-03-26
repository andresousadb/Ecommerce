from django import forms
from .models import Account, Profile
import re


def validar_celular(numero):
    padrao = r'^\(?[1-9]{2}\)? ?(?:[2-8]|9[1-9])[0-9]{3}-?[0-9]{4}$'
    # Verifica se o número corresponde ao padrão
    if re.match(padrao, numero):
        return True
    else:
        return False

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Digite a senha'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirme sua senha'
    }))

    class Meta:
        model = Account
        fields = ['f_name', 'l_name', 'email', 'tel']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['f_name'].widget.attrs['placeholder'] = 'Nome'
        self.fields['l_name'].widget.attrs['placeholder'] = 'Sobrenome'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['tel'].widget.attrs['placeholder'] = 'Telefone'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Account.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está cadastrado. Por favor, use outro email.',
                                        code='invalid')
        return email

    def clean_tel(self):
        tel = self.cleaned_data.get('tel')
        if Account.objects.filter(tel=tel).exists():
            raise forms.ValidationError('Este telefone já está cadastrado. Por favor, use outro telefone.', code='invalid')
        if not validar_celular(tel):
            raise forms.ValidationError('Por favor, insira um número de celular válido.', code='invalid')
        return tel


    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Senha não corresponde!')

class UserForm(forms.ModelForm): 
    class Meta:
        model = Account
        fields = ('f_name', 'l_name', 'tel')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('address', 'city', 'state')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'




        



