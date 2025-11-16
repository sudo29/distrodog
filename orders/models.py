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

        
# Inventory Management Models

class InventoryBatch(models.Model):
    """Batch inventory tracking for incoming and outgoing samples"""
    
    BATCH_TYPE_CHOICES = [
        ('incoming', 'Incoming from Supplier'),
        ('outgoing', 'Outgoing to Customer'),
    ]
    
    batch_id = models.CharField(max_length=100, unique=True)
    batch_type = models.CharField(max_length=20, choices=BATCH_TYPE_CHOICES)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    quantity = models.IntegerField(help_text="Total quantity in batch")
    
    # Supplier/Customer Info
    supplier_name = models.CharField(max_length=255, blank=True, null=True, help_text="For incoming batches")
    customer_name = models.CharField(max_length=255, blank=True, null=True, help_text="For outgoing batches")
    
    # Documentation
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="PO/Invoice number")
    notes = models.TextField(blank=True, null=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('received', 'Received'),
            ('verified', 'Verified'),
            ('stored', 'Stored'),
            ('shipped', 'Shipped'),
        ],
        default='pending'
    )
    
    # Tracking
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='batches_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    received_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['batch_type']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.batch_id} - {self.product.name} ({self.batch_type}) x{self.quantity}"


class InventorySample(models.Model):
    """Individual samples within a batch with barcode tracking"""
    
    batch = models.ForeignKey(InventoryBatch, on_delete=models.CASCADE, related_name='samples')
    sample_number = models.CharField(max_length=50)  # e.g., 1001-001, 1001-002
    barcode = models.CharField(max_length=255, unique=True, blank=True, null=True)
    
    # Sample Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('in_stock', 'In Stock'),
            ('allocated', 'Allocated to Order'),
            ('shipped', 'Shipped'),
            ('damaged', 'Damaged'),
            ('lost', 'Lost'),
        ],
        default='in_stock'
    )
    
    # Linked to Order (if outgoing to customer)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='samples')
    
    # Quality Check
    quality_checked = models.BooleanField(default=False)
    quality_checked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='samples_checked')
    quality_check_date = models.DateTimeField(blank=True, null=True)
    quality_notes = models.TextField(blank=True, null=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['batch', 'sample_number']
        indexes = [
            models.Index(fields=['batch']),
            models.Index(fields=['barcode']),
            models.Index(fields=['status']),
        ]
        unique_together = ['batch', 'sample_number']
    
    def save(self, *args, **kwargs):
        """Auto-generate barcode from batch_id and sample_number"""
        if not self.barcode:
            self.barcode = f"{self.batch.batch_id}-{self.sample_number}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.barcode or self.sample_number} - {self.batch.product.name} ({self.status})"


class InventoryScanLog(models.Model):
    """Audit trail for all inventory operations"""
    
    ACTION_CHOICES = [
        ('batch_received', 'Batch Received'),
        ('sample_scan', 'Sample Scanned'),
        ('quality_check', 'Quality Check'),
        ('allocated_to_order', 'Allocated to Order'),
        ('damage_report', 'Damage Reported'),
        ('sample_shipped', 'Sample Shipped'),
    ]
    
    sample = models.ForeignKey(InventorySample, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    scanned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    details = models.JSONField(blank=True, null=True, help_text="Additional data like location, condition")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Inventory Scan Logs'
        indexes = [
            models.Index(fields=['sample']),
            models.Index(fields=['action']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.sample.barcode} ({self.timestamp})"
        return f"Scan {self.id} - Order {self.order.id} - {self.action} ({self.scanned_at})"
