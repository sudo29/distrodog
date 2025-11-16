from django.contrib import admin
from .models import Product, Order, ImageAttachment, ScanL, InventoryBatch, InventorySample, InventoryScanLog


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'barcode', 'quantity', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'sku', 'barcode']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'sku', 'barcode', 'description')
        }),
        ('Inventory', {
            'fields': ('quantity',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'product', 'quantity', 'status', 'barcode', 'created_at']
    list_filter = ['status', 'created_at', 'product']
    search_fields = ['customer', 'barcode', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    fieldsets = (
        ('Order Details', {
            'fields': ('customer', 'product', 'quantity', 'barcode')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Audit Trail', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class ImageAttachmentInline(admin.TabularInline):
    model = ImageAttachment
    extra = 1
    readonly_fields = ['uploaded_at', 'uploaded_by']
    fields = ['image', 'uploaded_by', 'uploaded_at']


@admin.register(ImageAttachment)
class ImageAttachmentAdmin(admin.ModelAdmin):
    list_display = ['order', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at', 'order']
    search_fields = ['order__customer', 'order__barcode']
    readonly_fields = ['uploaded_at', 'uploaded_by']


@admin.register(ScanLog)
class ScanLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'barcode_data', 'action', 'scanned_by', 'scanned_at']
    list_filter = ['action', 'scanned_at', 'order']
    search_fields = ['barcode_data', 'order__customer', 'order__barcode']
    readonly_fields = ['scanned_at', 'order', 'barcode_data', 'action']
    date_hierarchy = 'scanned_at'

    def has_add_permission(self, request):
        # Scan logs are created automatically, not manually
        return False

    def has_change_permission(self, request, obj=None):
        # Scan logs should not be editable for audit purposes
        return False

    def has_delete_permission(self, request, obj=None):
        # Scan logs should not be deletable for audit purposes
        return False
