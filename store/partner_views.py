# store/partner_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings  # ADDED THIS IMPORT
from .models import Partner, PartnerSale, PartnerClick, Product, Category
import qrcode
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64
from django.core.files.base import ContentFile


def partner_landing(request, partner_code):
    """Landing page when someone scans a partner QR code"""
    try:
        partner = Partner.objects.get(partner_code=partner_code)
        
        # Check if partner is inactive
        if partner.status != 'active':
            messages.error(request, "This partner code is not active.")
            return redirect('store:product_list')
        
        # Check if QR code has expired
        if partner.qr_expiry_date and timezone.now() > partner.qr_expiry_date:
            messages.error(request, "This partner code has expired. Please contact the partner for a new code.")
            # Still track the attempted click for analytics
            PartnerClick.objects.create(
                partner=partner,
                session_key=request.session.session_key or 'anonymous',
                ip_address=get_client_ip(request),
                converted=False,
                clicked_at=timezone.now()
            )
            return redirect('store:product_list')
            
    except Partner.DoesNotExist:
        messages.error(request, "Invalid partner code.")
        return redirect('store:product_list')
    
    # Store partner code in session for commission tracking
    request.session['partner_code'] = partner_code
    request.session['partner_id'] = partner.id
    request.session.modified = True
    
    # Track the successful click
    PartnerClick.objects.create(
        partner=partner,
        session_key=request.session.session_key or 'anonymous',
        ip_address=get_client_ip(request),
        converted=False,
        clicked_at=timezone.now()
    )
    
    messages.success(request, f"Welcome! You've been referred by {partner.partner_name}")
    return redirect('store:product_list')


@login_required
def partner_dashboard(request):
    """Dashboard for partners to view their statistics"""
    try:
        partner = request.user.partner_profile
    except Partner.DoesNotExist:
        messages.error(request, "You don't have a partner account.")
        return redirect('store:product_list')
    
    if partner.status != 'active':
        messages.warning(request, "Your partner account is not active yet. Please wait for approval.")
        return redirect('store:product_list')
    
    # Generate QR code if it doesn't exist
    if not partner.qr_code_image:
        generate_partner_qr_code(partner)
    
    # Get statistics
    clicks = partner.clicks.count()
    sales = partner.sales.filter(status='completed').count()
    conversion_rate = (sales / clicks * 100) if clicks > 0 else 0
    
    # Recent sales
    recent_sales = partner.sales.all().order_by('-created_at')[:10]
    
    # Check if QR code is expired or expiring soon
    days_until_expiry = None
    if partner.qr_expiry_date:
        time_diff = partner.qr_expiry_date - timezone.now()
        days_until_expiry = time_diff.days if time_diff.days > 0 else 0
    
    context = {
        'partner': partner,
        'clicks': clicks,
        'sales': sales,
        'conversion_rate': conversion_rate,
        'recent_sales': recent_sales,
        'days_until_expiry': days_until_expiry,
    }
    
    return render(request, 'partner_dashboard.html', context)


def partner_register(request):
    """Registration form for new partners"""
    # Check if user is logged in
    if not request.user.is_authenticated:
        messages.warning(request, "Please login first to register as a partner.")
        return redirect('store:login')  # Redirect to your existing login page
    
    if hasattr(request.user, 'partner_profile'):
        messages.info(request, "You already have a partner account.")
        return redirect('store:partner_dashboard')
    
    if request.method == 'POST':
        # Get form data
        partner_name = request.POST.get('partner_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        
        # Create partner
        partner = Partner.objects.create(
            user=request.user,
            partner_name=partner_name,
            email=email,
            phone=phone,
            status='pending',
            commission_percentage=5.00,  # Default 5%
            total_sales=0,
            total_commission_earned=0,
            total_commission_paid=0,
            qr_validity_days=30  # Default 30 days expiry
        )
        
        messages.success(request, "Partner registration submitted! Awaiting approval.")
        return redirect('store:product_list')
    
    return render(request, 'partner_register.html')


def generate_partner_qr_code(partner):
    """Generate QR code for a partner"""
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    
    # CHANGED: Use dynamic URL based on environment
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    referral_url = f"{site_url}/partner/{partner.partner_code}/"
    
    qr.add_data(referral_url)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    
    # Save to model
    file_name = f'{partner.partner_code}_qr.png'
    partner.qr_code_image.save(file_name, ContentFile(buffer.getvalue()), save=True)
    
    # Set expiry date if not already set
    if partner.qr_validity_days > 0 and not partner.qr_expiry_date:
        from datetime import timedelta
        partner.qr_expiry_date = timezone.now() + timedelta(days=partner.qr_validity_days)
        partner.save()
    
    return partner.qr_code_image


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '0.0.0.0'


@login_required
def admin_partner_list(request):
    """Admin view to manage partners"""
    if not request.user.is_staff:
        messages.error(request, "You don't have permission.")
        return redirect('store:product_list')
    
    partners = Partner.objects.all()
    
    if request.method == 'POST':
        partner_id = request.POST.get('partner_id')
        action = request.POST.get('action')
        
        partner = get_object_or_404(Partner, id=partner_id)
        
        if action == 'approve':
            partner.status = 'active'
            # Set expiry date on approval
            if partner.qr_validity_days > 0:
                from datetime import timedelta
                partner.qr_expiry_date = timezone.now() + timedelta(days=partner.qr_validity_days)
            partner.save()
            # Generate QR code for approved partner
            generate_partner_qr_code(partner)
            messages.success(request, f"Partner {partner.partner_name} approved!")
        elif action == 'deactivate':
            partner.status = 'inactive'
            partner.save()
            messages.success(request, f"Partner {partner.partner_name} deactivated!")
        elif action == 'extend':
            # Extend expiry by 30 days
            from datetime import timedelta
            if partner.qr_expiry_date:
                partner.qr_expiry_date += timedelta(days=30)
            else:
                partner.qr_expiry_date = timezone.now() + timedelta(days=30)
            partner.is_expired = False
            partner.save()
            messages.success(request, f"Extended expiry for {partner.partner_name} by 30 days!")
        
        return redirect('store:admin_partner_list')
    
    return render(request, 'admin_partner_list.html', {'partners': partners})