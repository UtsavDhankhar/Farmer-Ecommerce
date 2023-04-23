from django.contrib import admin
from .models import Payment , Order , OrderProduct
# Register your models here.

#for inline table
class orderProductAdmin(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment' , 'user' , 'product' , 'quantity' , 'product_price')
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number' , 'user' , 'address' , 'is_ordered' ,'order_total' ]
    list_per_page = 20
    list_filter = ['is_ordered' , 'status']
    inlines = [orderProductAdmin]


admin.site.register(Payment)
admin.site.register(Order , OrderAdmin)
admin.site.register(OrderProduct)