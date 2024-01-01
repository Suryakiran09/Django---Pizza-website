from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import Product, Cart, CartItem, Address
from django.db.models import Sum
from .forms import AddressForm
from django.views.decorators.csrf import csrf_exempt
from .models import Order
import razorpay
import random
import uuid
from django.http import JsonResponse


def user_login(request):
    if request.user.is_authenticated:
            return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login/login.html', {'error_message': 'Invalid username or password'})

    return render(request, 'login/login.html')

def registration(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        retype_password = request.POST.get('retype_password')

       
        if password == retype_password:
            
            if User.objects.filter(username=email).exists():
                messages.success(request, "User with this email already exists.")
            else:
                # Create user and log in
                user = User.objects.create_user(username=email, first_name=first_name, last_name=last_name, email=email, password=password)
                user.save()
                authenticated_user = authenticate(request, username=email, password=password)
                login(request, user)
                return redirect('home') 
        else:
            messages.error(request, "Password and Retype Password do not match.")
    return render(request,'registration/registration.html')


def user_logout(request):
    logout(request)
    return redirect("/login")


@login_required(login_url='login')
def home(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request,'product/product.html', context)

@login_required(login_url='login')
def add_to_cart(request, product_id):
    product = Product.objects.get(pk=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the item is already in the cart
    cart_item, item_created = CartItem.objects.get_or_create(product=product, cart=cart)

    if not item_created:
        # If the item already exists in the cart, increase the quantity
        cart_item.quantity += 1
        cart_item.save()

    # messages.success(request, "Item added to cart successfully.")
    return redirect('home')

# @login_required(login_url='login')
# def view_cart(request):
#     cart, created = Cart.objects.get_or_create(user=request.user)
#     cart_items = CartItem.objects.filter(cart=cart)
    
#     # Calculate the total cost using aggregation
#     total_cost = cart_items.aggregate(Sum('product__price'))['product__price__sum'] or 0
#     total_cost = round(total_cost,2)

#     return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_cost': total_cost})

@login_required(login_url='login')
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Calculate the total cost based on the quantity of each item
    total_cost = sum(item.product.price * item.quantity for item in cart_items)
    total_cost = round(total_cost, 2)

    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_cost': total_cost})


@login_required(login_url='login')
def remove_from_cart(request, cart_item_id):
    cart_item = CartItem.objects.get(pk=cart_item_id)
    cart_item.delete()
    # messages.success(request, "Item removed from cart.")
    return redirect('view_cart')


def update_quantity(request, cart_item_id, action):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1

    cart_item.save()

    # Calculate the total cost based on the quantity of each item
    cart_items = CartItem.objects.filter(cart=cart_item.cart)
    total_cost = sum(item.product.price * item.quantity for item in cart_items)
    total_cost = round(total_cost, 2)

    cart_item.cart.total_cost = total_cost
    cart_item.cart.save()

    # messages.success(request, "Quantity updated successfully.")
    return redirect('view_cart')

@login_required(login_url='login')
def update_address(request):
    user = request.user
    address_instance, created = Address.objects.get_or_create(user=user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address_instance)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to the home page after address update
    else:
        form = AddressForm(instance=address_instance)

    return render(request, 'update_address.html', {'form': form})

client = razorpay.Client(auth=("rzp_test_t9uknc2io8QnuI", "OOCypKPUSQB2YUJeWb6QXvSC"))


# Initialize Razorpay client
client = razorpay.Client(auth=("rzp_test_t9uknc2io8QnuI", "OOCypKPUSQB2YUJeWb6QXvSC"))

@csrf_exempt
@login_required(login_url='login')
def initiate_payment(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    # Calculate total amount for the order
    total_amount = round(sum(item.product.price * item.quantity for item in cart_items), 2)
    
    # Ensure that the total amount is at least 1.00
    if total_amount < 1.00:
        total_amount = 1.00

    # Convert the total amount to paise for Razorpay
    total_amount_paise = int(total_amount * 100)

    # Create a Razorpay order
    data = {
        "amount": total_amount_paise,
        "currency": "INR",
        "receipt": f"ord_{uuid.uuid4().hex[:8]}",
    }
    order = client.order.create(data=data)

    # Save the Razorpay order ID to the order model
    new_order = Order.objects.create(
        user=request.user,
        product=cart_items.first().product,  # Assuming all items in the cart belong to the same product
        quantity=cart_items.aggregate(Sum('quantity'))['quantity__sum'],
        total_amount=total_amount,
        razorpay_order_id=order['id'],
    )

    # Clear the cart after successful order initiation
    cart_items.delete()

    return render(request, 'payment.html', {'order': new_order})


@csrf_exempt
def handle_payment_success(request):
    # This view handles the success callback from Razorpay after a successful payment
    if request.method == 'POST':
        order_id = request.POST.get('razorpay_order_id')
        signature = request.POST.get('razorpay_signature')

        try:
            # Verify the payment signature
            client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': request.POST.get('razorpay_payment_id'),
                'razorpay_signature': signature,
            })

            # Update order status to 'Shipped' after successful payment
            order = Order.objects.get(razorpay_order_id=order_id)
            order.order_status = 'Shipped'
            order.save()

            # Clear user's cart after successful payment
            request.user.cartitem.delete()

            messages.success(request, 'Payment successful! Your order is on the way.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Payment failed: {str(e)}')
            return redirect('view_cart')
    else:
        return redirect('home')