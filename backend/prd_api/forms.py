from django import forms


class add_prd(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    description = forms.CharField(widget=forms.Textarea, max_length=3000, required=True)
    price = forms.IntegerField(min_value=0, required=True)
    currency_type = forms.ChoiceField(required=True)
    image = forms.ImageField(required=False)
    category = forms.ChoiceField(required=True)
    digital_file = forms.FileField(required=False)
    file_format = forms.CharField(max_length=10, required=False)
    file_size = forms.IntegerField(min_value=0, required=False)
    tags = forms.CharField(max_length=200, required=False)
    license_type = forms.CharField(max_length=50, required=False)
    is_free = forms.BooleanField(required=False)

class edit_prd(forms.Form):
    id = forms.IntegerField(required=True)
    name = forms.CharField(max_length=50, required=True)
    description = forms.CharField(widget=forms.Textarea, max_length=3000, required=True)
    price = forms.IntegerField(min_value=0, required=True)
    currency_type = forms.ChoiceField(required=True)
    image = forms.ImageField(required=False)
    category = forms.ChoiceField(required=True)
    digital_file = forms.FileField(required=False)
    file_format = forms.CharField(max_length=10, required=False)
    file_size = forms.IntegerField(min_value=0, required=False)
    tags = forms.CharField(max_length=200, required=False)
    license_type = forms.CharField(max_length=50, required=False)
    is_free = forms.BooleanField(required=False)