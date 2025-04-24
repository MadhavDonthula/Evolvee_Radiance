# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Collection, Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal

# Create a custom form that extends UserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
import boto3
from django.conf import settings

# Initialize S3 client
s3_client = boto3.client(
    's3',
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    collections = Collection.objects.all()
    products = Product.objects.filter(available=True)
    featured_products = Product.objects.filter(available=True, is_featured=True)[:4]
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'product_list.html', {
        'category': category,
        'categories': categories,
        'collections': collections,
        'products': products,
        'featured_products': featured_products
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    
    # Get related products
    related_products = Product.objects.filter(
        Q(category=product.category) | Q(collection=product.collection)
    ).exclude(id=product.id).filter(available=True)[:4]
    
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def search(request):
    return render(request, 'search.html')

def checkout(request):
    return render(request, 'checkout.html')

def saved_items(request):
    return render(request, 'saved_items.html')



# Simple cart functions using Django session
def get_cart(request):
    """Get or initialize the cart in session"""
    if 'cart' not in request.session:
        request.session['cart'] = {}
    return request.session['cart']

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