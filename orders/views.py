from django.shortcuts import render , redirect
from django.contrib.auth.decorators import login_required
from carts.models import Cart , CartItem , address
from orders.forms import OrderForm
from store.models import Product
from .models import Order , Payment ,OrderProduct
import calendar
import datetime
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from django.http import JsonResponse


def mail(request , user , email , mail_subject , link , order):
    message = render_to_string(link , {
        'user' : user,
        'order' : order
    })
    to_email = email
    send_email = EmailMessage(mail_subject,
                            message,
                            settings.EMAIL_HOST_USER,
                            to = [to_email],
                            )
    send_email.fail_silently = False
    send_email.send()
    return


def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    total = 0
    quantity = 0

    if(cart_count <= 0):
        return redirect ('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity

    tax = (2*total)/100
    grand_total = total + tax


    if(request.method == 'POST'):
        print("in post")
        address_id = request.POST['address']
        address_order = address.objects.get(id = address_id)

        data = Order(
            user = request.user,
            address = address_order,
            order_note = request.POST['order_note'],
            order_total = grand_total,
            tax = tax,
            ip = request.META.get('REMOTE_ADDR')
        )
        
        data.save()

        #using data id and unix timestamp to generate unique order id
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        order_number = str(utc_time) + str(data.id)
        data.order_number = order_number
        data.save()

        order = Order.objects.get(user = current_user , is_ordered = False , order_number = order_number)
        
        page_dict = {
            'order' : order,
            'cart_items' : cart_items,
            'total' : total,
            'tax' : tax,
            'gtotal' : grand_total,
        }

        return render(request , 'orders/payment.html' , page_dict)
          
    else:
        return redirect('home')


def payment(request):
    body = json.loads(request.body)
    order = Order.objects.get(user = request.user , order_number = body['orderID'])
    
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )

    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.status = 'Completed'
    order.save()

    # Move cart items to orderProduct
    cart_items = CartItem.objects.filter(user = request.user)

    for item in cart_items:
        orderProduct = OrderProduct()
        orderProduct.order_id = order.id
        orderProduct.payment_id = payment
        orderProduct.user_id = request.user.id
        orderProduct.product_id = item.product_id
        orderProduct.quantity = item.quantity
        orderProduct.product_price = item.product.price
        orderProduct.ordered = True
        orderProduct.save()

        product_variation = item.variations.all()
        orderProduct.variations.set(product_variation)
        orderProduct.save()

        #reduce product quantity

        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear Cart Items
    cart_items.delete() 

    # Send Mail
    user = request.user
    email = request.user.email
    mail_subject = "Thank You for ordering from our website"
    link = 'orders/order_recieved.html'
    mail(request , user , email , mail_subject , link , order)


    #Send order number and transaction id back to send Data method via JSONResponse
    data = {
        'order_number' : order.order_number,
        'trans_id' : payment.payment_id
    }
    return JsonResponse(data)


def order_complete(request):

    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number = order_number , is_ordered = True)
        ordered_product = OrderProduct.objects.filter(order_id = order.id)
        payment = Payment.objects.get(payment_id = payment_id)
        sub_total = order.order_total - order.tax
        page_dict = {
            'order' : order,
            'payment' : payment,
            'ordered_product' : ordered_product, 
            'sub_total' : sub_total,
        }

        return render(request , 'orders/order_complete.html' ,page_dict)

    except (Order.DoesNotExist , Payment.DoesNotExist):
        return redirect('home')
    
    