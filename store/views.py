# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Collection, Product
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q

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
<<<<<<< HEAD
    return render(request, 'store/product_detail.html', {'product': product})

def search(request):
    return render(request, 'store/search.html')

def checkout(request):
    return render(request, 'store/checkout.html')

def saved_items(request):
    return render(request, 'store/saved_items.html')
    
# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import cv2
import base64

=======
    
    # Get related products
    related_products = Product.objects.filter(
        Q(category=product.category) | Q(collection=product.collection)
    ).exclude(id=product.id).filter(available=True)[:4]
    
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products
    })

def registerPage(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get("username")
            messages.success(request, f"Account was created for {user}")
            return redirect("store:login")
    context = {"form": form}
    return render(request, "register.html", context)

def loginPage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:  # Check if user is admin
                return redirect("admin:index")  # Redirect to admin page
            return redirect("store:product_list")  # Redirect to homepage
        else:
            messages.info(request, "Username or password is incorrect")
    return render(request, "login.html")

def logoutUser(request):
    logout(request)
    return redirect("loginPage")
>>>>>>> 39480b0 (adding_products)
