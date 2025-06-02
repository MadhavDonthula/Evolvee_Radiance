# store/models.py
from django.db import models
from django.urls import reverse
from .models import Category

def categories(request):
    return {
        'categories': Category.objects.all()
    }
