# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, SavedItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

# Create a custom form that extends UserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    featured_products = Product.objects.filter(available=True, is_featured=True)[:4]
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
        'featured_products': featured_products
    })

@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    is_saved = SavedItem.objects.filter(user=request.user, product=product).exists()

    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
        'is_saved': is_saved,
    })

# store/views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def toggle_save_item(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        saved_item, created = SavedItem.objects.get_or_create(user=request.user, product=product)

        if not created:
            saved_item.delete()
            return JsonResponse({'saved': False})
        return JsonResponse({'saved': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def search(request):
    return render(request, 'search.html')

def checkout(request):
    return render(request, 'checkout.html')

@login_required
def saved_items(request):
    saved = SavedItem.objects.filter(user=request.user).select_related('product')
    return render(request, 'saved_items.html', {'saved_items': saved})



# Simple cart functions using Django session
def get_cart(request):
    """Get or initialize the cart in session"""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']
@csrf_protect
def add_to_cart(request, product_id):
    """Add a product to the cart"""
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = get_cart(request)
    
    # Get quantity from form, default to 1
    quantity = int(request.POST.get('quantity', 1))
    
    # Convert product_id to string since session keys must be strings
    product_id_str = str(product_id)
    
    # If product already in cart, update quantity
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        # Add product to cart
        cart[product_id_str] = {
            'quantity': quantity,
            'price': str(product.price)
        }
    
    # Save changes to session
    request.session.modified = True
    
    # Redirect to cart page
    return redirect('store:cart_detail')

def remove_from_cart(request, product_id):
    """Remove a product from the cart"""
    cart = get_cart(request)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session.modified = True
    
    return redirect('store:cart_detail')

def cart_detail(request):
    """Show cart contents"""
    cart = get_cart(request)
    cart_items = []
    total_price = Decimal('0')
    
    # Process each cart item and fetch product data
    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            price = Decimal(item_data['price'])
            quantity = item_data['quantity']
            total_item_price = price * quantity
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
                'total_price': total_item_price
            })
            
            total_price += total_item_price
            
        except Product.DoesNotExist:
            # Remove the product if it no longer exists in the database
            del cart[product_id]
            request.session.modified = True
    
    # Make sure we render to the correct template path
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@csrf_protect
def register_view(request):
    if request.user.is_authenticated:
        return redirect('store:product_list')  # Homepage
    
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Automatically log in the user after successful registration
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created successfully.')
            return redirect('store:product_list')  # Redirect to homepage instead of login
        else:
            messages.error(request, "Please correct the errors below.")
    
    return render(request, 'register.html', {'form': form})

# Login View
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('store:product_list')  # Homepage
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('store:product_list')  # Replace with your homepage view name
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'login.html')

# Logout View
@login_required
@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('store:login')

@csrf_protect
def category_products_page(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, available=True)
    categories = Category.objects.all()
    return render(request, 'products_page.html', {
        'category': category,
        'products': products,
        'categories': categories,
    })

@login_required
def about_view(request):
    return render(request, 'about_us.html')