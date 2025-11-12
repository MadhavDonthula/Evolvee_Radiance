# store/urls.py
from django.urls import path
from . import views
from . import partner_views  

# handles URLs specific to the store
app_name = 'store'

urlpatterns = [
    # Existing URLs
    path('', views.product_list, name='product_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('checkout/', views.shopify_checkout, name='shopify_checkout'),
    path('saved-items/', views.saved_items, name='saved_items'),
    
    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('apply-partner-code/', views.apply_partner_code, name='apply_partner_code'),  # NEW LINE ADDED
    path('save-product/', views.toggle_save_item, name='toggle_save_item'),

    path('category/<slug:category_slug>/products/', views.category_products_page, name='category_products_page'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_us, name='contact_us'),
    
    # Debug endpoint (remove in production)
    path('debug-s3/', views.debug_s3, name='debug_s3'),
    
    # Partner URLs
    path('partner/<str:partner_code>/', partner_views.partner_landing, name='partner_landing'),
    path('partner-register/', partner_views.partner_register, name='partner_register'),
    path('partner-dashboard/', partner_views.partner_dashboard, name='partner_dashboard'),
    path('admin/partners/', partner_views.admin_partner_list, name='admin_partner_list'),
]