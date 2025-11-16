#!/usr/bin/env python
"""Setup script to generate all missing Django project files."""
import os

print("\n=== DistRodog Project Setup ===")
print("Creating missing files...\n")

# Create directories
os.makedirs('orders/migrations', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)
os.makedirs('media', exist_ok=True)
os.makedirs('templates', exist_ok=True)

# distrodog/urls.py
with open('distrodog/urls.py', 'w') as f:
    f.write("""from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [path('admin/', admin.site.urls)]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
""")
print("✓ Created distrodog/urls.py")

# distrodog/asgi.py
with open('distrodog/asgi.py', 'w') as f:
    f.write("""import os
from django.core.asgi import get_asgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'distrodog.settings')
application = get_asgi_application()
""")
print("✓ Created distrodog/asgi.py")

# distrodog/wsgi.py
with open('distrodog/wsgi.py', 'w') as f:
    f.write("""import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'distrodog.settings')
application = get_wsgi_application()
""")
print("✓ Created distrodog/wsgi.py")

# orders/__init__.py
with open('orders/__init__.py', 'w') as f:
    f.write("""# Orders Django app\n""")
print("✓ Created orders/__init__.py")

# orders/migrations/__init__.py
with open('orders/migrations/__init__.py', 'w') as f:
    f.write("""""")
print("✓ Created orders/migrations/__init__.py")

# orders/models.py
with open('orders/models.py', 'w') as f:
    f.write("""from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=128, unique=True)
    barcode = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f\"{self.name} ({self.sku})\"

class Order(models.Model):
    STATUS_CHOICES = [('new','New'),('processing','Processing'),('packed','Packed'),('shipped','Shipped'),('delivered','Delivered'),('cancelled','Cancelled')]
    customer = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=64, choices=STATUS_CHOICES, default='new')
    barcode = models.CharField(max_length=128, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    def __str__(self):
        return f\"Order {self.id} - {self.customer}\"

class ImageAttachment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='order_images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class ScanLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='scan_logs')
    barcode_data = models.CharField(max_length=128)
    scanned_at = models.DateTimeField(auto_now_add=True)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=64)
""")
print("✓ Created orders/models.py")

# orders/admin.py
with open('orders/admin.py', 'w') as f:
    f.write("""from django.contrib import admin
from .models import Product, Order, ImageAttachment, ScanLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'barcode', 'quantity', 'created_at')
    search_fields = ('name', 'sku', 'barcode')
    list_filter = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'product', 'quantity', 'status', 'created_at')
    search_fields = ('customer', 'barcode', 'product__name')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ImageAttachment)
class ImageAttachmentAdmin(admin.ModelAdmin):
    list_display = ('order', 'uploaded_at', 'uploaded_by')
    search_fields = ('order__id',)

@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ('order', 'barcode_data', 'action', 'scanned_at', 'scanned_by')
    search_fields = ('order__id', 'barcode_data')
    list_filter = ('action', 'scanned_at')
""")
print("✓ Created orders/admin.py")

print("\n=== Setup Complete ===")
print("\nNext steps:")
print("1. python manage.py migrate")
print("2. python manage.py createsuperuser")
print("3. python manage.py runserver")
print("\nThen visit: http://localhost:8000/admin")
