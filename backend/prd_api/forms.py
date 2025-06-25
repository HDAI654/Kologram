from django import forms


class add_prd(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    discription = forms.CharField(max_length=3000, required=True)
    price = forms.IntegerField(required=True)
    currency_type = forms.CharField(max_length=20, required=True)
    image = forms.ImageField(required=False)

class edit_prd(forms.Form):
    id = forms.IntegerField(required=True)
    name = forms.CharField(max_length=50, required=True)
    discription = forms.CharField(max_length=3000, required=True)
    price = forms.IntegerField(required=True)
    currency_type = forms.CharField(max_length=20, required=True)
    image = forms.ImageField(required=False)