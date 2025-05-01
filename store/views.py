from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, EmailAuthenticationForm
from django.contrib.auth.decorators import login_required

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})

def login_view(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('store:product_list')
    else:
        form = EmailAuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('store:login')  
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})
    
def search(request):
    return render(request, 'store/search.html')

def checkout(request):
    return render(request, 'store/checkout.html')

def saved_items(request):
    return render(request, 'store/saved_items.html')

@login_required
def profile_view(request):
    return render(request, 'store/profile.html', {'user': request.user})

def logout_view(request):
    logout(request)
    return redirect('store:product_list')
    
# Additional imports for handling JSON responses and CSRF exemptions
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
import cv2
import base64