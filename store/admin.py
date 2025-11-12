# store/admin.py
from django.contrib import admin
from .models import Category, Product, Partner, PartnerSale, PartnerClick, PartnerPayment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'available', 'shopify_variant_id']
    list_filter = ['available', 'category']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    fieldsets = (
        (None, {
            'fields': ('category', 'name', 'slug', 'image', 'price', 'stock', 'available', 'shopify_variant_id')
        }),
        ('Description', {
            'fields': ('description', 'tagline')
        }),
    )

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ['partner_name', 'partner_code', 'status', 'commission_percentage', 
                    'qr_validity_days', 'qr_expiry_date', 'is_expired']
    list_filter = ['status', 'is_expired', 'created_at']
    search_fields = ['partner_name', 'email', 'partner_code']
    readonly_fields = ['partner_code', 'is_expired', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Partner Information', {
            'fields': ('user', 'partner_name', 'partner_code', 'email', 'phone', 'address')
        }),
        ('Commission & Status', {
            'fields': ('status', 'commission_percentage', 'payment_method', 'payment_details')
        }),
        ('QR Code Settings', {
            'fields': ('qr_validity_days', 'qr_expiry_date', 'is_expired', 'qr_code_image'),
            'description': 'Set validity_days to 0 for QR codes that never expire. Use "Regenerate QR codes" action for expired partners.'
        }),
        ('Financial Summary', {
            'fields': ('total_sales', 'total_commission_earned', 'total_commission_paid')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['approve_partners', 'deactivate_partners', 'extend_expiry_30_days', 'regenerate_qr_codes']
    
    def approve_partners(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        count = 0
        for partner in queryset:
            partner.status = 'active'
            # Set expiry date based on validity_days
            if partner.qr_validity_days > 0:
                partner.qr_expiry_date = timezone.now() + timedelta(days=partner.qr_validity_days)
            partner.save()
            # Generate QR code
            from .partner_views import generate_partner_qr_code
            generate_partner_qr_code(partner)
            count += 1
        self.message_user(request, f"{count} partners approved and QR codes generated.")
    
    def deactivate_partners(self, request, queryset):
        count = queryset.update(status='inactive')
        self.message_user(request, f"{count} partners deactivated.")
    
    def extend_expiry_30_days(self, request, queryset):
        from datetime import timedelta
        from django.utils import timezone
        count = 0
        for partner in queryset:
            if partner.qr_expiry_date:
                partner.qr_expiry_date += timedelta(days=30)
            else:
                partner.qr_expiry_date = timezone.now() + timedelta(days=30)
            partner.is_expired = False
            partner.save()
            count += 1
        self.message_user(request, f"Extended expiry by 30 days for {count} partners.")
    
    def regenerate_qr_codes(self, request, queryset):
        """Generate new partner codes and QR codes for selected partners"""
        count = 0
        for partner in queryset:
            old_code = partner.partner_code
            partner.regenerate_code()
            count += 1
            self.message_user(request, f"Partner {partner.partner_name}: {old_code} → {partner.partner_code}")
        self.message_user(request, f"Regenerated codes for {count} partners.", level='SUCCESS')
    
    approve_partners.short_description = "Approve selected partners"
    deactivate_partners.short_description = "Deactivate selected partners"
    extend_expiry_30_days.short_description = "Extend expiry by 30 days (same code)"
    regenerate_qr_codes.short_description = "🔄 Regenerate QR codes (NEW codes)"

@admin.register(PartnerSale)
class PartnerSaleAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'partner', 'total', 'commission_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order_id', 'partner__partner_name', 'customer_email']
    readonly_fields = ['created_at', 'completed_at']

@admin.register(PartnerClick)
class PartnerClickAdmin(admin.ModelAdmin):
    list_display = ['partner', 'clicked_at', 'ip_address', 'converted']
    list_filter = ['converted', 'clicked_at']
    search_fields = ['partner__partner_name', 'ip_address']
    readonly_fields = ['clicked_at', 'converted_at']

@admin.register(PartnerPayment)
class PartnerPaymentAdmin(admin.ModelAdmin):
    list_display = ['partner', 'amount', 'status', 'period_start', 'period_end', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['partner__partner_name', 'transaction_id']
    readonly_fields = ['created_at', 'paid_at']