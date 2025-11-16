from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.db.models import Q
import json
from .models import Product, Order, ImageAttachment, ScanLog


@login_required
def dashboard(request):
    """Main POS dashboard"""
    orders_today = Order.objects.filter(
        created_at__date=date.today()
    ).order_by('-created_at')
    
    stats = {
        'total_orders': Order.objects.count(),
        'orders_today': orders_today.count(),
        'pending_orders': Order.objects.filter(
            status__in=['new', 'processing']
        ).count(),
        'products': Product.objects.count(),
    }
    
    return render(request, 'orders/dashboard.html', {
        'orders': orders_today[:20],
        'stats': stats,
    })


@login_required
def order_list(request):
    """List all orders with filters"""
    orders = Order.objects.all().order_by('-created_at')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if status:
        orders = orders.filter(status=status)
    if search:
        orders = orders.filter(
            Q(customer__icontains=search) |
            Q(barcode__icontains=search) |
            Q(product__name__icontains=search)
        )
    
    return render(request, 'orders/order_list.html', {
        'orders': orders[:100],
        'selected_status': status,
    })


@login_required
def create_order(request):
    """Create new order (POS entry)"""
    if request.method == 'POST':
        return handle_create_order(request)
    
    products = Product.objects.all()
    return render(request, 'orders/create_order.html', {
        'products': products,
    })


def handle_create_order(request):
    """Handle order creation via form"""
    customer = request.POST.get('customer')
    product_id = request.POST.get('product')
    quantity = int(request.POST.get('quantity', 1))
    barcode = request.POST.get('barcode')
    notes = request.POST.get('notes')
    
    product = get_object_or_404(Product, id=product_id)
    
    order = Order.objects.create(
        customer=customer,
        product=product,
        quantity=quantity,
        barcode=barcode or f"ORD-{int(datetime.now().timestamp())}",
        notes=notes,
        created_by=request.user,
    )
    
    ScanLog.objects.create(
        order=order,
        barcode_data=order.barcode,
        scanned_by=request.user,
        action='order_created',
    )
    
    return redirect('order_detail', pk=order.id)


@login_required
def order_detail(request, pk):
    """View order details"""
    order = get_object_or_404(Order, id=pk)
    images = order.images.all()
    scans = order.scans.all().order_by('-scanned_at')
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'images': images,
        'scans': scans,
    })


@login_required
@require_http_methods(["POST"])
def update_order_status(request, pk):
    """Update order status"""
    order = get_object_or_404(Order, id=pk)
    new_status = request.POST.get('status')
    
    if new_status in dict(Order.STATUS_CHOICES):
        order.status = new_status
        order.save()
        
        ScanLog.objects.create(
            order=order,
            barcode_data=order.barcode,
            scanned_by=request.user,
            action='status_change',
            details={'new_status': new_status}
        )
        
        return redirect('order_detail', pk=order.id)
    
    return redirect('order_detail', pk=order.id)


@login_required
def barcode_scan(request):
    """Handle barcode scan entry"""
    if request.method == 'POST':
        barcode = request.POST.get('barcode').strip()
        
        try:
            order = Order.objects.get(barcode=barcode)
            return redirect('order_detail', pk=order.id)
        except Order.DoesNotExist:
            return render(request, 'orders/barcode_scan.html', {
                'error': f'Order with barcode {barcode} not found',
            })
    
    return render(request, 'orders/barcode_scan.html')


from datetime import date
from datetime import datetime
