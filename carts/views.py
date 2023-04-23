from django.http import HttpResponse
from django.shortcuts import render , redirect
from store.models import Product , Variation
from .models import Cart , CartItem , address
from .forms import AddressForm
from django.contrib.auth.decorators import login_required
from .forms import AddressForm
from orders.forms import OrderForm


def _cart_id(request):

    cart = request.session.session_key

    if not cart:
        cart = request.session.create()
    
    return cart


def add_cart(request , product_id):

    product = Product.objects.get(id=product_id)
    product_variation = []

    current_user = request.user

    if current_user.is_authenticated:
        if(request.method == "POST"):
            for item in request.POST:
                value = request.POST.get(item) 
                try:
                    variation = Variation.objects.get(product = product , variation_category__iexact = item , variation_value__iexact = value)
                    product_variation.append(variation)
                except:
                    pass


        is_cart_item_exits = CartItem.objects.filter(product = product , user = current_user)
        
        if is_cart_item_exits:
            cart_item = CartItem.objects.filter(product = product , user = current_user)

            exist_var_list = []
            id = []

            for item in cart_item:
                existin_variation = item.variations.all()
                exist_var_list.append(list(existin_variation))
                id.append(item.id)
            
            if product_variation in exist_var_list:
                index = exist_var_list.index(product_variation)
                cart_item[index].quantity +=1
                cart_item[index].save()
            
            else:
                cart_item = CartItem.objects.create(
                    product = product,
                    user = current_user,
                    quantity = 1
                )

                if len(product_variation):
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation) # instead of for loop just add *in front of list to add complete list

                cart_item.save()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                user = current_user,
                quantity = 1
            )

            if len(product_variation):
                for item in product_variation:
                    cart_item.variations.add(item)

            cart_item.save()

    else:

        if(request.method == "POST"):
            
            for item in request.POST:
                value = request.POST.get(item) 
                try:
                    variation = Variation.objects.get(product = product , variation_category__iexact = item , variation_value__iexact = value)
                    product_variation.append(variation)
                    print(product_variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id = _cart_id(request))

        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request),
            )  
        cart.save()

        is_cart_item_exits = CartItem.objects.filter(product = product , cart = cart)
        
        if is_cart_item_exits:
            cart_item = CartItem.objects.filter(product = product , cart = cart)

            exist_var_list = []
            id = []

            for item in cart_item:
                existin_variation = item.variations.all()
                exist_var_list.append(list(existin_variation))
                id.append(item.id)
            
            if product_variation in exist_var_list:
                index = exist_var_list.index(product_variation)
                cart_item[index].quantity +=1
                cart_item[index].save()
            
            else:
                cart_item = CartItem.objects.create(
                    product = product,
                    cart = cart,
                    quantity = 1
                )
                if len(product_variation):
                    cart_item.variations.clear()
                    # for item in product_variation:
                    #     cart_item.variations.add(item)
                    cart_item.variations.add(*product_variation) # instead of for loop just add *in front of list to add complete list

                cart_item.save()
        
        else:
            cart_item = CartItem.objects.create(
                product = product,
                cart = cart,
                quantity = 1
            )

            if len(product_variation):
                for item in product_variation:
                    cart_item.variations.add(item)

            cart_item.save()

    return redirect('cart')



def remove_cart(request , product_id , cart_item_id):
    
    product = Product.objects.get(id = product_id)

    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user = request.user , product = product , id = cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(cart = cart , product = product , id = cart_item_id) # since id is unique cart_item_id would have been enough

    if(cart_item.quantity > 1):
        cart_item.quantity -= 1
        cart_item.save()
    
    else:

        cart_item.delete()

    return redirect('cart')


def remove(request , product_id , cart_item_id):

    product = Product.objects.get(id = product_id)
    
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user = request.user , product = product , id = cart_item_id)
    else:
        cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_item = CartItem.objects.get(cart= cart , product = product , id = cart_item_id)

    cart_item.delete()

    return redirect('cart')



def cart(request):

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user = request.user)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart)

        quantity = 0
        total_price = 0

        for item in cart_items:
            quantity += item.quantity
            total_price += item.product.price * item.quantity
        
        tax = (total_price*8)/100

        total_after_tax = total_price + tax

    except Cart.DoesNotExist:
        tax = 0
        quantity = 0
        total_price  = 0
        total_after_tax = 0
        cart_items = None



    page_dict = {
        'cart_items' : cart_items,
        'quantity' : quantity,
        'total_price' : total_price,
        'tax' : tax,
        'total_after_tax' : total_after_tax,
        'path' : request.path

    }

    return render(request , 'carts/cart.html' , page_dict)



@login_required(login_url='login')
def checkout(request):

    try:
        # cart = Cart.objects.get(cart_id = _cart_id(request))
        cart_items = CartItem.objects.filter(user = request.user)
        addresses  = address.objects.filter(user = request.user)
        form = OrderForm()

        print(addresses)

        quantity = 0
        total_price = 0

        for item in cart_items:
            quantity += item.quantity
            total_price += item.product.price * item.quantity
        
        tax = (total_price*8)/100

        total_after_tax = total_price + tax

    except Cart.DoesNotExist:
        tax = 0
        quantity = 0
        total_price  = 0
        total_after_tax = 0
        cart_items = None



    page_dict = {
        'cart_items' : cart_items,
        'quantity' : quantity,
        'total_price' : total_price,
        'tax' : tax,
        'total_after_tax' : total_after_tax,
        'path' : request.path,
        'addresses' : addresses,
        'form': form,

    }

    return render(request , 'carts/checkout.html' , page_dict)

@login_required(login_url='login')
def address_page(request):

    if(request.method == 'POST'):
        form = AddressForm(request.POST)
        if(form.is_valid):
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('checkout')

    page_dict = {
        'form': AddressForm
    }

    return render(request , 'carts/address.html' , page_dict)