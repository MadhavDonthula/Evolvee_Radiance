# store/urls.py
from django.urls import path
from . import views

# handles URLs specific to the store
app_name = 'store'

urlpatterns = [
    # Existing URLs
    path('', views.product_list, name='product_list'),
    # path('login/', views.loginPage, name='login'),
    # path('register/', views.registerPage, name='register'),
    # path('logout/', views.logoutUser, name='logout'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('saved-items/', views.saved_items, name='saved_items'),
    
    # Cart URLs
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]