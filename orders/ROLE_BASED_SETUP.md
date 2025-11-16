# Role-Based Access Control Setup Guide

## Overview

This guide explains how to implement role-based access control (RBAC) for Distrodog POS so that users automatically see different dashboards based on their assigned role.

---

## Current Architecture

The dashboard currently shows all features to all authenticated users. This guide updates it to show role-specific features.

---

## Step 1: Create Django Groups (ADMIN ONLY)

Run these commands in your Docker container:

```bash
docker-compose exec web python manage.py shell
```

Then in Python shell:

```python
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from orders.models import Order, Product, ScanLog, ImageAttachment

# Create groups
managers_group, _ = Group.objects.get_or_create(name='managers')
operators_group, _ = Group.objects.get_or_create(name='operators')
warehouse_group, _ = Group.objects.get_or_create(name='warehouse_staff')

# Get permissions
add_order = Permission.objects.get(codename='add_order')
change_order = Permission.objects.get(codename='change_order')
delete_order = Permission.objects.get(codename='delete_order')
add_product = Permission.objects.get(codename='add_product')
change_product = Permission.objects.get(codename='change_product')
delete_product = Permission.objects.get(codename='delete_product')

# MANAGERS: Can view and update orders
managers_group.permissions.add(add_order, change_order)

# OPERATORS: Can create and update their own orders
operators_group.permissions.add(add_order, change_order)

# WAREHOUSE STAFF: Can update order status only
warehouse_group.permissions.add(change_order)

print("Groups created successfully!")
exit()
```

---

## Step 2: Assign Users to Roles

In Django Admin (`http://localhost:8000/admin/`):

1. Go to **Users**
2. Click user to edit
3. Scroll to **Groups**
4. Check the role:
   - ✅ managers
   - ✅ operators  
   - ✅ warehouse_staff
5. Click **Save**

**Example:**
- Manager: john_manager → check "managers"
- Operator: jane_operator → check "operators"
- Warehouse: bob_warehouse → check "warehouse_staff"

---

## Step 3: Update Dashboard Views (Add to views.py)

Add role-checking decorator to views:

```python
from django.contrib.auth.decorators import permission_required, login_required
from django.core.exceptions import PermissionDenied

def check_user_role(user):
    """Determine user role for dashboard"""
    if user.is_superuser:
        return 'admin'
    elif user.groups.filter(name='managers').exists():
        return 'manager'
    elif user.groups.filter(name='operators').exists():
        return 'operator'
    elif user.groups.filter(name='warehouse_staff').exists():
        return 'warehouse'
    return 'guest'

@login_required
def dashboard(request):
    """Main dashboard with role-based content"""
    user_role = check_user_role(request.user)
    from datetime import date
    
    context = {'user_role': user_role}
    
    if user_role == 'admin' or user_role == 'manager':
        # Show all orders
        context['stats'] = {
            'total_orders': Order.objects.count(),
            'orders_today': Order.objects.filter(created_at__date=date.today()).count(),
            'pending_orders': Order.objects.filter(status__in=['new', 'processing']).count(),
            'products': Product.objects.count(),
        }
        context['orders'] = Order.objects.all().order_by('-created_at')[:20]
        context['show_admin_panel'] = (user_role == 'admin')
        context['show_reports'] = True
        
    elif user_role == 'operator':
        # Show only user's orders
        context['stats'] = {
            'my_orders': Order.objects.filter(created_by=request.user).count(),
            'orders_today': Order.objects.filter(created_by=request.user, created_at__date=date.today()).count(),
            'my_pending': Order.objects.filter(created_by=request.user, status__in=['new', 'processing']).count(),
            'products': Product.objects.count(),
        }
        context['orders'] = Order.objects.filter(created_by=request.user).order_by('-created_at')[:20]
        context['show_create_order'] = True
        context['show_reports'] = False
        
    elif user_role == 'warehouse':
        # Show assigned orders only
        context['stats'] = {
            'assigned_orders': Order.objects.filter(status__in=['processing', 'packed']).count(),
            'ready_to_ship': Order.objects.filter(status='packed').count(),
        }
        context['orders'] = Order.objects.filter(status__in=['processing', 'packed']).order_by('-created_at')[:20]
        context['show_scan_interface'] = True
        context['show_proof_upload'] = True
    
    return render(request, 'orders/dashboard.html', context)
```

---

## Step 4: Update Dashboard Template

Update `templates/orders/dashboard.html` to use role-based rendering:

```django
{% if user_role == 'admin' %}
    {# Admin sees everything #}
    <div class="stat-card">
        <div class="stat-label">System Orders</div>
        <div class="stat-value">{{ stats.total_orders }}</div>
    </div>
    <a href="/admin/" class="btn btn-secondary">Admin Panel</a>
    
{% elif user_role == 'manager' %}
    {# Manager sees company-wide stats #}
    <div class="stat-card">
        <div class="stat-label">Total Orders</div>
        <div class="stat-value">{{ stats.total_orders }}</div>
    </div>
    <a href="/admin/orders/order/" class="btn btn-secondary">All Orders</a>
    
{% elif user_role == 'operator' %}
    {# Operator sees only their orders #}
    <div class="stat-card">
        <div class="stat-label">My Orders</div>
        <div class="stat-value">{{ stats.my_orders }}</div>
    </div>
    <a href="{% url 'orders:create_order' %}" class="btn btn-success">Create Order</a>
    
{% elif user_role == 'warehouse' %}
    {# Warehouse staff sees queue #}
    <div class="stat-card">
        <div class="stat-label">My Queue</div>
        <div class="stat-value">{{ stats.assigned_orders }}</div>
    </div>
    <a href="{% url 'orders:barcode_scan' %}" class="btn btn-secondary">Scan Barcode</a>
{% endif %}
```

---

## Step 5: Restrict Views by Permission

Add permission checks to view functions:

```python
@permission_required('orders.add_order', raise_exception=True)
def create_order(request):
    """Only operators and above can create orders"""
    # existing code

@permission_required('orders.delete_order', raise_exception=True)
def delete_order(request, pk):
    """Only admins can delete orders"""
    # existing code
```

---

## Step 6: Test Role-Based Access

**As Admin (root):**
```
http://localhost:8000/pos/
→ Should see Admin Panel link and all statistics
```

**As Manager:**
```
http://localhost:8000/pos/
→ Should see company statistics and reports
→ Should NOT see Admin Panel
```

**As Operator:**
```
http://localhost:8000/pos/
→ Should see "My Orders" only
→ Should see Create Order button
→ Should NOT see reports
```

**As Warehouse Staff:**
```
http://localhost:8000/pos/
→ Should see "My Queue"
→ Should see Scan Barcode button
→ Should NOT see Create Order
```

---

## Role Permission Summary

| Feature | Admin | Manager | Operator | Warehouse |
|---------|-------|---------|----------|----------|
| View All Orders | ✅ | ✅ | ❌ | ❌ |
| View My Orders | ✅ | ✅ | ✅ | ✅ |
| Create Order | ✅ | ✅ | ✅ | ❌ |
| Update Order | ✅ | ✅ | ✅ | ✅ (status only) |
| Delete Order | ✅ | ❌ | ❌ | ❌ |
| Manage Products | ✅ | ❌ | ❌ | ❌ |
| View Reports | ✅ | ✅ | ❌ | ❌ |
| Manage Users | ✅ | ❌ | ❌ | ❌ |
| Scan Barcode | ✅ | ✅ | ✅ | ✅ |
| Upload Images | ✅ | ✅ | ✅ | ✅ |

---

## Troubleshooting

### User not seeing role-based content
→ Check user is assigned to group in Admin Panel
→ User may need to logout/login to refresh permissions
→ Check browser cache

### Permission denied errors
→ Verify user group has required permissions
→ Check @permission_required decorators in views.py
→ Ensure groups were created in Step 1

### Groups not showing in Admin
→ Run migrations: `docker-compose exec web python manage.py migrate`
→ Restart container: `docker-compose restart web`

---

## Advanced: Custom Permissions

Create custom permissions for finer control:

```python
class Order(models.Model):
    # ... existing fields ...
    
    class Meta:
        permissions = (
            ("can_view_all_orders", "Can view all orders"),
            ("can_generate_reports", "Can generate reports"),
            ("can_upload_images", "Can upload order images"),
        )
```

Then assign these permissions to groups instead of standard CRUD permissions.

