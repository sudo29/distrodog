# Template Setup Guide - Distrodog POS

## Templates Already Created
✅ `templates/orders/base.html` - Base template with professional POS styling
✅ `templates/orders/dashboard.html` - Main dashboard with statistics

## Required Templates to Create

Create these files in `orders/templates/orders/` directory:

### 1. order_list.html
Template for displaying all orders with filtering and search.
- Shows all orders in a table
- Filter by status (new, processing, packed, shipped, delivered, cancelled)
- Search by customer name, barcode, or product
- Links to view order details

### 2. create_order.html
Template for creating new orders (POS entry form).
- Form fields: Customer name, Product (dropdown), Quantity, Barcode (auto-generated), Notes
- Submit button creates order
- Redirects to order detail on success

### 3. order_detail.html
Template displaying complete order details.
- Order info: Customer, Product, Quantity, Status, Barcode
- Status update dropdown with submit button
- Image attachments section (upload/view)
- Scan log table showing audit trail
- Back link to orders list

### 4. barcode_scan.html
Barcode scanner interface.
- Simple form for barcode input
- Auto-focus barcode field
- Looks up order by barcode
- Redirects to order detail on match
- Shows error if not found

## Fastest Way to Get Started

Run this command to access dashboard (even without remaining templates):

```bash
http://localhost:8000/pos/
```

The dashboard template is already created and will work immediately.
For other pages, use Django Admin:

```bash
http://localhost:8000/admin/
Orders section -> manage all orders
```

## Template Code Examples

### order_list.html
```django
{% extends 'orders/base.html' %}
{% block title %}Orders - Distrodog POS{% endblock %}
{% block content %}
<div class="card">
    <h1 class="card-title">📦 All Orders</h1>
    
    <form method="get" style="margin-bottom: 2rem;">
        <input type="text" name="search" placeholder="Search by customer, barcode, or product" value="{{ search }}" style="padding: 0.75rem; width: 300px; border: 1px solid #ddd; border-radius: 4px;">
        <select name="status" style="padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
            <option value="">-- All Status --</option>
            <option value="new" {% if selected_status == 'new' %}selected{% endif %}>New</option>
            <option value="processing" {% if selected_status == 'processing' %}selected{% endif %}>Processing</option>
            <option value="packed" {% if selected_status == 'packed' %}selected{% endif %}>Packed</option>
            <option value="shipped" {% if selected_status == 'shipped' %}selected{% endif %}>Shipped</option>
            <option value="delivered" {% if selected_status == 'delivered' %}selected{% endif %}>Delivered</option>
            <option value="cancelled" {% if selected_status == 'cancelled' %}selected{% endif %}>Cancelled</option>
        </select>
        <button type="submit" class="btn" style="padding: 0.75rem 1rem;">Search</button>
    </form>
    
    <table class="table">
        <thead>
            <tr>
                <th>Order</th>
                <th>Customer</th>
                <th>Product</th>
                <th>Qty</th>
                <th>Status</th>
                <th>Created</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>#{{ order.id }}</td>
                <td>{{ order.customer }}</td>
                <td>{{ order.product.name }}</td>
                <td>{{ order.quantity }}</td>
                <td>
                    {% if order.status == 'new' %}<span class="badge badge-info">New</span>
                    {% elif order.status == 'delivered' %}<span class="badge badge-success">Delivered</span>
                    {% elif order.status == 'cancelled' %}<span class="badge badge-danger">Cancelled</span>
                    {% else %}<span class="badge badge-warning">{{ order.get_status_display }}</span>{% endif %}
                </td>
                <td>{{ order.created_at|date:"M d, Y" }}</td>
                <td><a href="{% url 'orders:order_detail' order.id %}" class="btn" style="padding: 0.4rem 0.8rem; font-size: 0.9rem;">View</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}
```

### create_order.html
```django
{% extends 'orders/base.html' %}
{% block title %}Create Order - Distrodog POS{% endblock %}
{% block content %}
<div class="card">
    <h1 class="card-title">✅ Create New Order</h1>
    
    <form method="post" style="max-width: 600px;">
        {% csrf_token %}
        
        <div class="form-group">
            <label>Customer Name *</label>
            <input type="text" name="customer" placeholder="Enter customer name" required>
        </div>
        
        <div class="form-group">
            <label>Product *</label>
            <select name="product" required>
                <option value="">-- Select Product --</option>
                {% for product in products %}
                <option value="{{ product.id }}">{{ product.name }} (SKU: {{ product.sku }})</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label>Quantity *</label>
            <input type="number" name="quantity" value="1" min="1" required>
        </div>
        
        <div class="form-group">
            <label>Barcode (auto-generated if empty)</label>
            <input type="text" name="barcode" placeholder="Leave empty for auto-generation">
        </div>
        
        <div class="form-group">
            <label>Notes</label>
            <textarea name="notes" rows="4" placeholder="Add any notes for this order"></textarea>
        </div>
        
        <div style="display: flex; gap: 1rem;">
            <button type="submit" class="btn btn-success">Create Order</button>
            <a href="{% url 'orders:order_list' %}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

## Installation Instructions

1. Copy template code above
2. Create files in `orders/templates/orders/` directory via GitHub
3. Or download files and push to repository
4. Restart Docker container: `docker-compose restart web`
5. Access at http://localhost:8000/pos/

Dashboard is ready NOW - other templates optional (use admin panel as fallback)
