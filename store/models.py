# store/models.py
from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
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
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])
    
from django.contrib.auth.models import User

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