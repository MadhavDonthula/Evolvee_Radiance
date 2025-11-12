# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product, SavedItem, Partner  # Added Partner import
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from decimal import Decimal
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.utils import timezone  # ADD THIS IMPORT FOR EXPIRY CHECKING

# Create a custom form that extends UserCreationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm

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
    query = request.GET.get('q', '').strip()
    if query:
        product = Product.objects.filter(
            (Q(name__icontains=query) | Q(tagline__icontains=query) | Q(description__icontains=query)),
            available=True
        ).select_related('category').first()
        if product:
            # Redirect to the category products page for the product's category
            return redirect('store:category_products_page', category_slug=product.category.slug)
        else:
            categories = Category.objects.all()
            return render(request, 'search.html', {
                'query': query,
                'not_found': True,
                'categories': categories,
            })
    else:
        categories = Category.objects.all()
        return render(request, 'search.html', {'categories': categories})

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
    
    # Prefer explicit next url if provided
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    
    # Redirect back to referring page or category products page
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    else:
        return redirect('store:category_products_page', category_slug=product.category.slug)

def remove_from_cart(request, product_id):
    """Remove a product from the cart"""
    cart = get_cart(request)
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session.modified = True
    
    return redirect('store:cart_detail')

def cart_detail(request):
    """Show cart contents with partner discount if applicable"""
    cart = get_cart(request)
    cart_items = []
    subtotal = Decimal('0')
    
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
            
            subtotal += total_item_price
            
        except Product.DoesNotExist:
            del cart[product_id]
            request.session.modified = True
    
    # Check for partner discount with EXPIRY CHECK
    partner = None
    discount_amount = Decimal('0')
    partner_code = request.session.get('partner_code')
    
    if partner_code:
        try:
            partner = Partner.objects.get(partner_code=partner_code, status='active')
            
            # CHECK IF PARTNER CODE HAS EXPIRED
            if partner.qr_expiry_date and timezone.now() > partner.qr_expiry_date:
                # Code has expired - remove it from session
                messages.error(request, f"The partner code '{partner_code}' has expired and has been removed.")
                del request.session['partner_code']
                if 'partner_id' in request.session:
                    del request.session['partner_id']
                request.session.modified = True
                partner = None  # Don't apply discount
            else:
                # Code is valid and not expired - apply discount
                discount_amount = subtotal * (partner.commission_percentage / Decimal('100'))
                
        except Partner.DoesNotExist:
            # Invalid or inactive partner code
            messages.error(request, "Invalid or inactive partner code has been removed.")
            if 'partner_code' in request.session:
                del request.session['partner_code']
            if 'partner_id' in request.session:
                del request.session['partner_id']
            request.session.modified = True
    
    total_price = subtotal - discount_amount
    
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'partner': partner,
        'discount_amount': discount_amount,
        'total_price': total_price
    })

@csrf_protect
def apply_partner_code(request):
    """Apply a partner code manually with expiry check"""
    if request.method == 'POST':
        code = request.POST.get('partner_code', '').upper()
        
        if code:
            try:
                partner = Partner.objects.get(partner_code=code, status='active')
                
                # CHECK IF PARTNER CODE HAS EXPIRED
                if partner.qr_expiry_date and timezone.now() > partner.qr_expiry_date:
                    messages.error(request, f"This partner code has expired. Please contact {partner.partner_name} for a new code.")
                else:
                    # Code is valid and not expired
                    request.session['partner_code'] = code
                    request.session['partner_id'] = partner.id
                    request.session.modified = True
                    messages.success(request, f"Partner code applied! You'll get {partner.commission_percentage}% off")
                    
            except Partner.DoesNotExist:
                messages.error(request, "Invalid or inactive partner code")
        else:
            # Remove partner code if empty
            if 'partner_code' in request.session:
                del request.session['partner_code']
            if 'partner_id' in request.session:
                del request.session['partner_id']
            request.session.modified = True
            messages.info(request, "Partner code removed")
    
    return redirect('store:cart_detail')

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
    return redirect('store:product_list')

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

@login_required
def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            send_mail(
                cd['subject'],
                f"From: {cd['full_name']} <{cd['email']}>\n\n{cd['message']}",
                settings.DEFAULT_FROM_EMAIL,
                ['mdonthula98@gmail.com'],
            )
            messages.success(request, "Your message has been sent!")
            return redirect('store:contact_us')
    else:
        form = ContactForm()
    return render(request, 'contact_us.html', {'form': form})

def shopify_checkout(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        return redirect('store:cart')  # Empty cart fallback

    line_items = []

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            variant_id = product.shopify_variant_id
            quantity = item.get('quantity', 1)

            if variant_id:
                line_items.append(f"{variant_id}:{quantity}")
        except Product.DoesNotExist:
            continue  # Just skip missing or deleted products

    if not line_items:
        return redirect('store:cart')  # No valid variant IDs

    # Build Shopify cart URL
    cart_string = ",".join(line_items)
    shopify_url = f"https://p16t10-q1.myshopify.com/cart/{cart_string}"
    
    # Add partner code as a note if present (Shopify doesn't support discount codes via URL)
    partner_code = request.session.get('partner_code')
    if partner_code:
        # Note: Shopify doesn't support discount codes via cart URL
        # need to handle this differently, perhaps with Shopify webhooks
        pass
    
    return redirect(shopify_url)

# Debug view for S3 configuration (remove in production)
from django.http import JsonResponse
from django.conf import settings

def debug_s3(request):
    """Debug view to check S3 configuration"""
    data = {
        'USE_S3': getattr(settings, 'USE_S3', False),
        'AWS_ACCESS_KEY_ID': '✓ Set' if getattr(settings, 'AWS_ACCESS_KEY_ID', '') else '✗ Missing',
        'AWS_SECRET_ACCESS_KEY': '✓ Set' if getattr(settings, 'AWS_SECRET_ACCESS_KEY', '') else '✗ Missing',
        'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '✗ Missing'),
        'AWS_S3_REGION_NAME': getattr(settings, 'AWS_S3_REGION_NAME', '✗ Missing'),
        'DEFAULT_FILE_STORAGE': getattr(settings, 'DEFAULT_FILE_STORAGE', '✗ Missing'),
        'MEDIA_URL': getattr(settings, 'MEDIA_URL', '✗ Missing'),
        'MEDIA_ROOT': str(getattr(settings, 'MEDIA_ROOT', '✗ Missing')),
    }
    return JsonResponse(data, indent=2)