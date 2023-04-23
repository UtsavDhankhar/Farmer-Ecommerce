from django import forms
from .models import Order

class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['order_note' , 'address']


    def __init__(self , *args, **kwargs):
        super(OrderForm, self).__init__(*args , **kwargs)

        self.fields['order_note'].widget.attrs['class'] = 'form-control'
        self.fields['address'].widget.attrs['class'] = 'form-control'