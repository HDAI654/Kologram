from django import forms

class login_form(forms.Form):
    def __init__(self, *args, **kwargs):
        super(login_form, self).__init__(*args, **kwargs)
        # set form-control class for each element
        for item in self.visible_fields():
            item.field.widget.attrs['class'] = 'form-control mt-2 mb-2'
            
    username = forms.CharField(max_length=50, required=True)
    password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput)


class reg_form(forms.Form):
    def __init__(self, *args, **kwargs):
        super(reg_form, self).__init__(*args, **kwargs)
        # set form-control class for each element
        for item in self.visible_fields():
            item.field.widget.attrs['class'] = 'form-control mt-2 mb-2'
            
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput)
    email = forms.EmailField(max_length=30, required=True)
