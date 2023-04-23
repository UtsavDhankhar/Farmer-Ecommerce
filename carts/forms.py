from .models import address
from django import forms

class AddressForm(forms.ModelForm):

    class Meta:
        model = address
        fields = ['first_name' , 'last_name' , 'phone_number' , 'address_line' , 'address_line_2' , 'city' , 'state' , 'country']


    def __init__(self , *args, **kwargs):
        super(AddressForm , self).__init__(*args , **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
