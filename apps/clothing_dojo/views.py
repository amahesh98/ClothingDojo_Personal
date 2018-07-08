from django.shortcuts import render, redirect, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from apps.clothing_admin.models import *
from apps.clothing_dojo.models import *
from djangounchained_flash import ErrorManager, getFromSession
from django.conf import settings
import stripe
import re

FREE_SHIRT_ID=1
stripe.api_key=settings.STRIPE_SECRET

# def loginPage(request):
#     # return render(request, 'clothing_dojo/login_page.html')
#     return render(request, 'clothing_dojo/clothingDojo_login.html')

# def processLogin(request):
#     request.session['loggedIn']=True
#     request.session['userID']=1
#     return redirect('/')

def logout(request):

    if('loggedIn' in request.session and request.session['loggedIn']==False):
        return redirect('/login/')
    if ('loggedIn' not in request.session):
        return redirect('/login/')
    request.session['adminLoggedIn']=False
    remember=request.session['remember']
    log_em=request.session['login_email']
    request.session.clear()
    request.session['remember']=remember
    request.session['login_email']=log_em
    print('Logging out')
    # return redirect('https://learn.codingdojo.com/')
    return redirect('/login/')

def index(request):
    # ADD to every view
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    if len(User.objects.filter(id=request.session['userID']))==0:
        return redirect('/login/')

    if 'flash' not in request.session:
        request.session['flash']=ErrorManager().addToSession()
    e=getFromSession(request.session['flash'])
    context={
        'products':Product.objects.all(),
        'user':User.objects.get(id=request.session['userID']),
        'shirt_success':e.getMessages('shirt_success'),
        'shirt_fail':e.getMessages('shirt_fail'),
    }
    request.session['flash']=e.addToSession()
    return render(request, 'clothing_dojo/clothingDojo_main.html', context)

def productPage(request, product_id):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')

    if len(Product.objects.filter(id=product_id))==0:
        print('Attempting to view product that does not exist')
        return redirect('/')
    context={
        'product':Product.objects.get(id=product_id),
        'other_products':Product.objects.exclude(id=product_id)[:4],
        'user':User.objects.get(id=request.session['userID'])
    }
    return render(request, 'clothing_dojo/clothingDojo_productPage.html', context)

def addToCart(request, product_id):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')

    if len(Product.objects.filter(id=product_id))==0:
        print('Attempting to view product that does not exist')
        return redirect('/')
    try:
        User.objects.get(id=request.session['userID']).cart
    except ObjectDoesNotExist:
        print("User ", request.session['userID'], 'has no cart')
        c=Cart(user=User.objects.get(id=request.session['userID']))
        c.save()
    print('Adding item ', Product.objects.get(id=product_id).name, ' to cart.')
    cart=User.objects.get(id=request.session['userID']).cart
    total=Product.objects.get(id=product_id).cost * int(request.POST['quantity'])
    CartItem.objects.create(cart=cart, product=Product.objects.get(id=product_id), color=Color.objects.get(id=request.POST['color']), size=request.POST['size'], quantity=request.POST['quantity'], total=total)
    cart.total+=total
    cart.save()
    e=getFromSession(request.session['flash'])
    string='Successfully added '+Product.objects.get(id=product_id).name+' to cart.'
    e.addMessage(string, 'cart_success')
    request.session['flash']=e.addToSession()
    return redirect('/cart/')

def cart(request):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    try:
        User.objects.get(id=request.session['userID']).cart
    except ObjectDoesNotExist:
        print("User ", request.session['userID'], 'has no cart')
        c=Cart(user=User.objects.get(id=request.session['userID']))
        c.save()
    count=0
    for item in User.objects.get(id=request.session['userID']).cart.items.all():
        count+=item.quantity
    e=getFromSession(request.session['flash'])
    showCheckout=0
    if len(User.objects.get(id=request.session['userID']).cart.items.all()):
        showCheckout=1
    context={
        
        'cart_success':e.getMessages('cart_success'),
        'cart':User.objects.get(id=request.session['userID']).cart,
        'count':count,
        'show_checkout':showCheckout,
        'user':User.objects.get(id=request.session['userID'])
    }
    request.session['flash']=e.addToSession()
    return render(request, 'clothing_dojo/clothingDojo_cart.html', context)

def removeFromCart(request, cartitem_id):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    if len(CartItem.objects.filter(id=cartitem_id))==0:
        print('No such cart item')
        return redirect('/cart/')
    print('Removing item from cart')
    e=getFromSession(request.session['flash'])
    e.addMessage('Successfully deleted item from cart', 'cart_success')
    request.session['flash']=e.addToSession()
    c=CartItem.objects.get(id=cartitem_id)
    cart=c.cart
    cart.total-=c.total
    cart.save()
    c.delete()
    return redirect('/cart/')

def checkout(request):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    try:
        User.objects.get(id=request.session['userID']).cart
    except ObjectDoesNotExist:
        print("User ", request.session['userID'], 'has no cart')
        c=Cart(user=User.objects.get(id=request.session['userID']))
        c.save()
        return redirect('/cart/')
    if len(User.objects.get(id=request.session['userID']).cart.items.all())==0:
        print('Cannot checkout on an empty cart')
        return redirect('/cart/')
    print('Checking out')
    # return redirect('/processCheckout/')
    return redirect('/payment/')

def paymentInfo(request):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    try:
        User.objects.get(id=request.session['userID']).cart
    except ObjectDoesNotExist:
        print("User ", request.session['userID'], 'has no cart')
        c=Cart(user=User.objects.get(id=request.session['userID']))
        c.save()
        return redirect('/cart/')
    count=0
    for item in User.objects.get(id=request.session['userID']).cart.items.all():
        count+=item.quantity
    e=getFromSession(request.session['flash'])
    context={
        'user':User.objects.get(id=request.session['userID']),
        'cart':User.objects.get(id=request.session['userID']).cart,
        'count':count,
        'card_fail':e.getMessages('card_fail'),
        'month_fail':e.getMessages('month_fail'),
        'year_fail':e.getMessages('year_fail'),
        'cvv_fail':e.getMessages('cvv_fail'),
        'publishable':settings.STRIPE_PUBLISHABLE,
    }
    request.session['flash']=e.addToSession()
    return render(request, 'clothing_dojo/clothingDojo_payment.html', context)

def processCheckout(request):
    print('Processing Checkout')
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    try:
        User.objects.get(id=request.session['userID']).cart
    except ObjectDoesNotExist:
        print("User ", request.session['userID'], 'has no cart')
        c=Cart(user=User.objects.get(id=request.session['userID']))
        c.save()
        return redirect('/cart/')
    if len(User.objects.get(id=request.session['userID']).cart.items.all())==0:
        print('Cannot checkout on an empty cart')
        return redirect('/cart/')

    cart=User.objects.get(id=request.session['userID']).cart
    o=Order(user=User.objects.get(id=request.session['userID']), total=0, location=User.objects.get(id=request.session['userID']).cohort.location)
    o.save()
    for item in cart.items.all():
        ot=OrderItem.objects.create(product=item.product, order=o, size=item.size, color=item.color, quantity=item.quantity, total=item.total)
        o.total+=ot.total
        o.num_items+=ot.quantity
        p=ot.product
        p.num_sold+=ot.quantity
        p.save()

    location=User.objects.get(id=request.session['userID']).cohort.location
    o.batch=location.batches.last()
    o.save()
    
    for item in o.items.all():
        if len(location.batches.last().items.filter(product=item.product, size=item.size, color=item.color))==0:
            bt=BatchItem.objects.create(product=item.product, batch=location.batches.last(), size=item.size, color=item.color, quantity=item.quantity, total=item.total)
        else:
            bt=location.batches.last().items.get(product=item.product, size=item.size, color=item.color)
            bt.quantity+=item.quantity
            bt.total+=item.total
            bt.save()

    print('Checkout successful')
    cart.delete()
    e=getFromSession(request.session['flash'])
    e.addMessage('Your order has been successfully placed!','shirt_success')
    request.session['flash']=e.addToSession()
    return redirect('/')

def claimShirt(request):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    if User.objects.get(id=request.session['userID']).claimed_shirt==True:
        print('User has already claimed shirt')
        e=getFromSession(request.session['flash'])
        e.addMessage('You have already ordered your free shirt.', 'shirt_fail')
        request.session['flash']=e.addToSession()
        return redirect('/')
    context={
        'user':User.objects.get(id=request.session['userID']),
        'product':Product.objects.get(id=FREE_SHIRT_ID)
    }
    return render(request, 'clothing_dojo/clothingDojo_freeShirt.html', context)

def processClaim(request):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    if User.objects.get(id=request.session['userID']).claimed_shirt==True:
        print('User has already claimed shirt')
        e=getFromSession(request.session['flash'])
        e.addMessage('You have already ordered your free shirt.', 'shirt_fail')
        request.session['flash']=e.addToSession()
        return redirect('/')
    if request.method!='POST':
        return redirect('/')
    o=Order(user=User.objects.get(id=request.session['userID']), total=0, location=User.objects.get(id=request.session['userID']).cohort.location)
    o.save()
    shirt=Product.objects.get(id=FREE_SHIRT_ID)
    OrderItem.objects.create(product=shirt, order=o, size=request.POST['size'], color=Color.objects.get(id=request.POST['color']), quantity=1, total=0)
    o.num_items=1
    shirt.num_sold+=1
    shirt.save()
    location=User.objects.get(id=request.session['userID']).cohort.location
    o.batch=location.batches.last()
    o.save()
    user=User.objects.get(id=request.session['userID'])
    user.claimed_shirt=True
    user.save()
    
    if len(location.batches.last().items.filter(product=shirt, size=request.POST['size'], color=Color.objects.get(id=request.POST['color'])))==0:
        bt=BatchItem.objects.create(product=shirt, batch=location.batches.last(), size=request.POST['size'], color=Color.objects.get(id=request.POST['color']), quantity=1, total=0)
    else:
        bt=location.batches.last().items.get(product=shirt, size=request.POST['size'], color=Color.objects.get(id=request.POST['color']))
        bt.quantity+=1
        bt.save()

    e=getFromSession(request.session['flash'])
    e.addMessage('Your shirt has been successfully claimed.', 'shirt_success')
    request.session['flash']=e.addToSession()
    print('Successfully claimed shirt')
    return redirect('/')

def viewOrders(request):
    print('Viewing orders')
    # return HttpResponse('Hello')
    return render(request, 'clothing_dojo/clothingDojo_viewOrders.html')

def processPayment(request):
    if 'loggedIn' not in request.session:
        return redirect('/login/')
    if request.session['loggedIn']==False:
        return redirect('/login/')
    if 'userID' not in request.session:
        return redirect('/login/')
    if request.method!='POST':
        return redirect('/')
    try:
        User.objects.get(id=request.session['userID']).cart
    except ObjectDoesNotExist:
        print("User ", request.session['userID'], 'has no cart')
        c=Cart(user=User.objects.get(id=request.session['userID']))
        c.save()
        return redirect('/cart/')
    if len(User.objects.get(id=request.session['userID']).cart.items.all())==0:
        print('Cannot checkout on an empty cart')
        return redirect('/cart/')

    # DATA VALIDATIONS
    e=getFromSession(request.session['flash'])
    validForm=True
    CARD_REGEX=re.compile(r'^[0-9]*$')
    if len(request.POST['card_number'])<9:
        e.addMessage('Invalid card number.', 'card_fail')
        validForm=False
    elif not CARD_REGEX.match(request.POST['card_number']):
        e.addMessage('Invalid card number.', 'card_fail')
        validForm=False
    if len(request.POST['exp_month'])==0:
        e.addMessage('Expiration month cannot be empty.', 'month_fail')
        validForm=False
    elif not request.POST['exp_month'].isdigit():
        e.addMessage('Invalid expiration month.', 'month_fail')
        validForm=False
    if len(request.POST['exp_year'])==0:
        e.addMessage('Expiration year cannot be empty.', 'year_fail')
        validForm=False
    elif not request.POST['exp_month'].isdigit():
        e.addMessage('Invalid expiration year.', 'year_fail')
        validForm=False
    if len(request.POST['cvv'])==0:
        e.addMessage('CVV cannot be empty.', 'cvv_fail')
        validForm=False
    elif not request.POST['cvv'].isdigit():
        e.addMessage('Invalid CVV.', 'cvv_fail')
        validForm=False
    
    if(validForm==False):
        request.session['flash']=e.addToSession()
        return redirect('/payment/')
    print(request.POST)
    try:
        customer=stripe.Charge.create(
            amount=int(User.objects.get(id=request.session['userID']).cart.total*100),
            currency='USD',
            description=User.objects.get(id=request.session['userID']).email,
            card=request.POST['stripe_id']
        )
        return redirect('/processCheckout/')
    except stripe.CardError as error:
        e.addMessage('The card has been declined', 'card_fail')
        request.session['flash']=e.addToSession()
        return redirect('/payment/')
    #FORM IS VALID
    print(request.POST)
    return redirect('/processCheckout/')
