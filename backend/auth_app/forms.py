from django import forms

class login_form(forms.Form):
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput)


class reg_form(forms.Form):            
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput)
    email = forms.EmailField(max_length=30, required=True)
