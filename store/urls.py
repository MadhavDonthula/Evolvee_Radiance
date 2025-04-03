# store/urls.py
from django.urls import path
from . import views

# handles URLs specific to the store
app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('saved-items/', views.saved_items, name='saved_items'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
]