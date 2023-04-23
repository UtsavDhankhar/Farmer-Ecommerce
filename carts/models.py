from django.db import models
from store.models import Product , Variation
from accounts.models import Account

# Create your models here.

class Cart(models.Model):

    cart_id = models.CharField(max_length=250 , blank = True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id



class CartItem(models.Model):
    user = models.ForeignKey(Account , on_delete=models.CASCADE , blank=True , null = True)
    product = models.ForeignKey(Product , on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart , on_delete=models.CASCADE , blank= True , null = True)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)


    def sub_total(self):

        return self.product.price * self.quantity


class address(models.Model):
    user = models.ForeignKey(Account , on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20 ,null = True , blank=True)
    address_line = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100 , blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)

    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def full_address(self):
        return f'{self.address_line}  {self.address_line_2}'

    def __str__(self):
        return self.first_name + self.last_name

