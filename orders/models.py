from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Product(models.Model):
    """Product catalog with barcode tracking"""
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=100, unique=True)
    barcode = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.name} ({self.sku})"


class Order(models.Model):
    """Order management with complete audit trail"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('processing', 'Processing'),
        ('packed', 'Packed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.CharField(max_length=255)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    barcode = models.CharField(max_length=255, unique=True)
    notes = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['barcode']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Order {self.id} - {self.customer} ({self.status})"


class ImageAttachment(models.Model):
    """Image attachments for order documentation"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='order_images/%Y/%m/%d/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name_plural = 'Image Attachments'

    def __str__(self):
        return f"Image for Order {self.order.id} - {self.uploaded_at}"


class ScanLog(models.Model):
    """Complete audit trail for all scans and actions"""
    ACTION_CHOICES = [
        ('scan', 'Barcode Scan'),
        ('status_change', 'Status Change'),
        ('image_upload', 'Image Upload'),
        ('note_added', 'Note Added'),
        ('order_created', 'Order Created'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='scans')
    barcode_data = models.CharField(max_length=255)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    scanned_at = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ['-scanned_at']
        verbose_name_plural = 'Scan Logs'
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['action']),
            models.Index(fields=['-scanned_at']),
        ]

    def __str__(self):
        return f"Scan {self.id} - Order {self.order.id} - {self.action} ({self.scanned_at})"
