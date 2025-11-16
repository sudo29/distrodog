from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpResponseForbidden
from django.views import View
from django.utils.decorators import method_decorator
from django.db.models import Q
from datetime import date, datetime
import json
from .models import Product, Order, ImageAttachment, ScanLog

# Role-based access control helper function
def get_user_role(user):
    """Get the role of a user based on their groups."""
    if not user.is_authenticated:
        return None
    
    # Super users are admins
    if user.is_superuser:
        return 'admin'
    
    # Check user groups
    groups = user.groups.values_list('name', flat=True)
    if 'administrators' in groups:
        return 'admin'
    elif 'managers' in groups:
        return 'manager'
    elif 'operators' in groups:
        return 'operator'
    elif 'warehouse_staff' in groups:
        return 'warehouse_staff'
    
    return 'guest'

def role_required(*allowed_roles):
    """Decorator to check if user has one of the allowed roles."""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            user_role = get_user_role(request.user)
            if user_role not in allowed_roles:
                return HttpResponseForbidden("You don't have permission to access this page.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@login_required
def dashboard(request):
    """Main POS dashboard with role-based content."""
    user_role = get_user_role(request.user)
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
    
    # Role-based context modifications
    context = {
        'orders': orders_today[:20],
        'stats': stats,
        'user_role': user_role,
    }
    
    # Add role-specific data
    if user_role in ['admin', 'manager']:
        context['total_revenue'] = sum(o.quantity for o in Order.objects.all())
        context['pending_count'] = stats['pending_orders']
    
    if user_role == 'admin':
        context['total_users'] = Order.objects.values('created_by').distinct().count()
    
    return render(request, 'orders/dashboard.html', context)

@login_required
@role_required('admin', 'manager', 'operator')
def order_list(request):
    """List all orders with filters."""
    user_role = get_user_role(request.user)
    orders = Order.objects.all().order_by('-created_at')
    
    # Warehouse staff can only see their own orders
    if user_role == 'warehouse_staff':
        orders = orders.filter(created_by=request.user)
    
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
        'user_role': user_role,
    })

@login_required
@role_required('admin', 'manager', 'operator')
def create_order(request):
    """Create new order (POS entry)."""
    if request.method == 'POST':
        return handle_create_order(request)
    
    products = Product.objects.all()
    return render(request, 'orders/create_order.html', {
        'products': products,
        'user_role': get_user_role(request.user),
    })

@login_required
@role_required('admin', 'manager', 'operator')
def handle_create_order(request):
    """Handle order creation via form."""
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
    """View order details."""
    user_role = get_user_role(request.user)
    order = get_object_or_404(Order, id=pk)
    
    # Warehouse staff can only view their own orders
    if user_role == 'warehouse_staff' and order.created_by != request.user:
        return HttpResponseForbidden("You don't have permission to view this order.")
    
    images = order.images.all()
    scans = order.scans.all().order_by('-scanned_at')
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'images': images,
        'scans': scans,
        'user_role': user_role,
    })

@login_required
@require_http_methods(["POST"])
@role_required('admin', 'manager')
def update_order_status(request, pk):
    """Update order status (manager/admin only)."""
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

@login_required
@role_required('admin', 'manager', 'operator', 'warehouse_staff')
def barcode_scan(request):
    """Handle barcode scan entry."""
    user_role = get_user_role(request.user)
    
    if request.method == 'POST':
        barcode = request.POST.get('barcode').strip()
        
        try:
            order = Order.objects.get(barcode=barcode)
            
            # Warehouse staff can only scan their own orders
            if user_role == 'warehouse_staff' and order.created_by != request.user:
                return render(request, 'orders/barcode_scan.html', {
                    'error': 'You can only scan orders you created.',
                    'user_role': user_role,
                })
            
            return redirect('order_detail', pk=order.id)
        except Order.DoesNotExist:
            return render(request, 'orders/barcode_scan.html', {
                'error': f'Order with barcode {barcode} not found',
                'user_role': user_role,
            })
    
    return render(request, 'orders/barcode_scan.html', {
        'user_role': get_user_role(request.user),
    })
