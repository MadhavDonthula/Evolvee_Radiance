# store/models.py
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import uuid
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_list_by_category', args=[self.slug])

class Collection(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, related_name='products', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image = models.ImageField(upload_to='products/')
    description = models.TextField()
    tagline = models.CharField(max_length=200, blank=True, help_text="Short description for product card (e.g. 'Signature crystal accent')")
    kit = models.CharField(max_length=200, blank=True, help_text="Product kit name (e.g. 'Crystal Couture Lip Kit')")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_featured = models.BooleanField(default=False, help_text="Feature this product on the homepage")
    has_led = models.BooleanField(default=False, help_text="Product has LED technology")
    stock = models.IntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    shopify_variant_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Paste the Shopify Variant ID (from Shopify admin URL)"
    )
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

class SavedItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} saved {self.product.name}"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')


# ============== PARTNER SYSTEM MODELS ==============

class Partner(models.Model):
    """Model for managing partners/affiliates"""
    PARTNER_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Approval'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='partner_profile')
    partner_name = models.CharField(max_length=200, help_text="Business or Partner Name")
    partner_code = models.CharField(max_length=50, unique=True, editable=False)
    commission_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=10.00,
        help_text="Commission percentage (e.g., 10.00 for 10%)"
    )
    status = models.CharField(max_length=20, choices=PARTNER_STATUS, default='pending')
    
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    payment_method = models.CharField(
        max_length=50,
        choices=[
            ('bank_transfer', 'Bank Transfer'),
            ('paypal', 'PayPal'),
            ('venmo', 'Venmo'),
            ('check', 'Check'),
        ],
        default='bank_transfer'
    )
    payment_details = models.TextField(blank=True)
    
    total_sales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_commission_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_commission_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    qr_code_image = models.ImageField(upload_to='partner_qr_codes/', blank=True, null=True)
    
    # QR Code Expiry Fields 
    qr_validity_days = models.IntegerField(
        default=30,
        help_text="Number of days the QR code is valid (0 = never expires)"
    )
    qr_expiry_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When the QR code expires. Auto-calculated from validity_days"
    )
    is_expired = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.partner_name} ({self.partner_code})"
    
    def save(self, *args, **kwargs):
        if not self.partner_code:
            self.partner_code = self.generate_partner_code()
        
        # Set expiry date when partner is approved
        if self.status == 'active' and self.qr_validity_days > 0 and not self.qr_expiry_date:
            from django.utils import timezone
            from datetime import timedelta
            self.qr_expiry_date = timezone.now() + timedelta(days=self.qr_validity_days)
        
        # Check if expired
        if self.qr_expiry_date:
            from django.utils import timezone
            self.is_expired = timezone.now() > self.qr_expiry_date
            
        super().save(*args, **kwargs)
    
    def generate_partner_code(self):
        """Generate a unique partner code"""
        base_code = self.partner_name[:3].upper() if self.partner_name else "PTR"
        unique_id = str(uuid.uuid4())[:6].upper()
        return f"{base_code}-{unique_id}"
    
    def get_referral_url(self):
        """Get the partner's referral URL"""
        from django.urls import reverse
        return f"/partner/{self.partner_code}/"
    
    def calculate_pending_commission(self):
        """Calculate pending commission to be paid"""
        return self.total_commission_earned - self.total_commission_paid
    
    def regenerate_code(self):
        """Generate completely new partner code and QR"""
        # Delete old QR image if it exists
        if self.qr_code_image:
            self.qr_code_image.delete()
        
        # Generate new partner code
        self.partner_code = self.generate_partner_code()
        
        # Reset expiry based on validity days
        if self.qr_validity_days > 0:
            from django.utils import timezone
            from datetime import timedelta
            self.qr_expiry_date = timezone.now() + timedelta(days=self.qr_validity_days)
        else:
            self.qr_expiry_date = None
        
        self.is_expired = False
        self.save()
        
        # Generate new QR code
        from store.partner_views import generate_partner_qr_code
        generate_partner_qr_code(self)


class PartnerSale(models.Model):
    """Track individual sales made through partner referrals"""
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='sales')
    order_id = models.CharField(max_length=100, unique=True)
    customer_email = models.EmailField(blank=True)
    
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    session_key = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    products_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Sale {self.order_id} - {self.partner.partner_name}"


class PartnerClick(models.Model):
    """Track clicks/visits from partner QR codes and links"""
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='clicks')
    session_key = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    
    converted = models.BooleanField(default=False)
    sale = models.ForeignKey(PartnerSale, null=True, blank=True, on_delete=models.SET_NULL)
    
    clicked_at = models.DateTimeField(auto_now_add=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-clicked_at']
    
    def __str__(self):
        return f"Click from {self.partner.partner_name} at {self.clicked_at}"


class PartnerPayment(models.Model):
    """Track payments made to partners"""
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    period_start = models.DateField()
    period_end = models.DateField()
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    
    processed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment of ${self.amount} to {self.partner.partner_name}"