from django import forms
from .models import Account, Profile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm password'
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

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError('Password does not match!')

class UserForm(forms.ModelForm): 
    class Meta:
        model = Account
        fields = ('f_name', 'l_name', 'email', 'tel')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('address', 'city', 'state','country')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'




        



