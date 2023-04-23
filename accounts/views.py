from django.shortcuts import render , redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required

#mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

#for cart
from carts.models import Cart , CartItem
from carts.views import _cart_id

import requests # download using pip install requests


def mail(request , user , email , mail_subject , link):

    current_site = get_current_site(request)
    message = render_to_string(link , {
        'user' : user,
        'domain' : current_site,
        'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
        'token' : default_token_generator.make_token(user),
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



def register(request):

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]

            user = Account.objects.create_user(first_name = first_name , last_name = last_name , email = email , username = username , password = password)
            user.phone_number = phone_number

            user.save()  

            # email service
            mail_subject = 'Account Activation'
            link = 'accounts/account_verification.html'
            mail(request , user , email , mail_subject , link)

            return redirect('/accounts/login/' + '?command=verification&email='+email)  #while redirecting always use /before otherwise django tends to take it as relative url

    else:
        form = RegistrationForm()
    
    page_dict = {
        'form' : form,
    }
    return render(request , 'accounts/register.html' , page_dict)



def login(request):

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email = email , password = password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                if CartItem.objects.filter(cart = cart).exists():
                    cart_items = CartItem.objects.filter(cart = cart)

                    product_variations = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variations.append(list(variation))
                    
                    cart_items = CartItem.objects.filter(user = user)
                    exist_var_list = []
                    id = []

                    for item in cart_items:
                        existin_variation = item.variations.all()
                        exist_var_list.append(list(existin_variation))
                        id.append(item.id)

                    
                    for i in product_variations:
                        if i in exist_var_list:
                            index = exist_var_list.index(i)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quantity +=1
                            item.user = user
                            item.save()
                        
                        else:
                            cart_items = CartItem.objects.filter(cart = cart)
                            for item in cart_items:
                                item.user = user
                                # item.cart.clear()
                                item.save()            
            except:
                pass

            auth.login(request , user)
            messages.success(request , 'Account is Logged In')
            url = request.META.get('HTTP_REFERER')  # this will give the url of page from which request was called.
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))

                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)

            except:
                return redirect('dashboard')

        else:

            messages.warning(request , 'Invalid Login Credentials')
            return redirect('login')

    return render(request , 'accounts/login.html')



@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request , "Logout Succesfull")
    return redirect('login')



def activate(request , uidb64 , token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid) #verifying the user

    except(TypeError , ValueError , OverflowError , Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user , token):
        user.is_active = True
        user.save()
        messages.success(request , 'Account is activated')
        return redirect('login')

    else:
        messages.error(request , 'Invalid Link')
        return redirect('register')



@login_required(login_url = 'login')
def dashboard(request):
    return render(request , 'accounts/dashboard.html')
    

def forgot_password(request):

    if request.method == 'POST':
        email = request.POST['email']  

        if Account.objects.filter(email__exact = email).exists():

            user = Account.objects.get(email = email)
            mail_subject = 'Reset Password'
            link = 'accounts/reset_password_email.html'
            mail(request , user , email , mail_subject , link)

            messages.success(request , 'Password reset email has been sent to your email address.')
            return redirect('login')

        else:
            messages.warning(request , 'Account Does not exist')
            return redirect('forgot_password')
    

    return render(request, 'accounts/forgot_password.html')



def reset_password_validate(request , uidb64 , token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk = uid)
    
    except(TypeError , ValueError , OverflowError , Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user , token):
        request.session['uid'] = uid
        return redirect('reset_password')

    messages.warning(request , 'Link has expired')
    return redirect('login')


def reset_password(request):

    if request.method == 'POST':
        try:
            uid = request.session['uid']
            user = Account.objects.get(pk = uid)
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            print(password + " " + confirm_password)

            if password == confirm_password:
                user.set_password(confirm_password)
                user.save()
                messages.success(request , 'Password Reset Successfull')
                return redirect ('login')
            
            else:
                request.session['uid'] = uid
                messages.warning(request , 'Password Does Not Match')
                return redirect('reset_password')
        
        except:
            messages.warning(request , 'Some error occured. Please try again later')
            return redirect('forgot_password')
    
    else:
        return render(request , 'accounts/reset_password.html')




