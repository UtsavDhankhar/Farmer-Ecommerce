from django.urls import path
from . import views


urlpatterns = [
    path('', views.cart , name = 'cart'),
    path('add_cart/<int:product_id>/' , views.add_cart , name = 'add_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/' , views.remove_cart , name = 'remove_cart'),
    path('remove/<int:product_id>/<int:cart_item_id>' , views.remove , name = 'remove'),
    path('checkout' , views.checkout , name = 'checkout'),
    path('address_page/' , views.address_page , name = 'address_page')
]