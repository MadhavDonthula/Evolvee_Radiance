# store/admin.py
from django.contrib import admin
from .models import Category, Collection, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'collection', 'price', 'stock', 'available', 'is_featured', 'created']
    list_filter = ['available', 'created', 'updated', 'category', 'collection', 'is_featured', 'has_led']
    list_editable = ['price', 'stock', 'available', 'is_featured']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    raw_id_fields = ['category', 'collection']
    fieldsets = (
        (None, {
            'fields': ('category', 'collection', 'name', 'slug', 'image', 'price', 'stock', 'available')
        }),
        ('Description', {
            'fields': ('description', 'tagline')
        }),
        ('Product Details', {
            'fields': ('kit', 'is_featured', 'has_led')
        }),
    )