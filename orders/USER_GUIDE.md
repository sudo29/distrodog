# Distrodog POS - Complete User Guide

## 🎯 Quick Start

**Main Entry Point:** `http://localhost:8000/pos/`

All users start at the **Dashboard** which automatically shows features based on their role.

---

## 👥 User Roles & Permissions

### 1. **Superuser/Administrator** 👨‍💼
**Permissions:** Full system access

**Features Available:**
- ✅ View all statistics and analytics
- ✅ Create/edit/delete orders
- ✅ Create/edit/delete products
- ✅ Manage users and permissions
- ✅ View complete audit logs (ScanLog)
- ✅ Generate reports
- ✅ System configuration

**Dashboard Access:**
- **📊 Main Dashboard** → Statistics, recent orders
- **👥 User Management** → Create users, set roles
- **📦 Inventory** → Add/edit products
- **📋 All Orders** → Full order list with all filters
- **📈 Reports** → Sales, delivery status, trends
- **⚙️ Settings** → System configuration

**Direct Links:**
```
http://localhost:8000/pos/               # Main dashboard
http://localhost:8000/admin/             # Full admin panel
```

---

### 2. **Manager/Supervisor** 📊
**Permissions:** View & update orders, manage staff

**Features Available:**
- ✅ View all orders and statistics
- ✅ Update order status
- ✅ View analytics and reports
- ✅ Manage staff (limited)
- ✅ View audit logs
- ❌ Cannot delete orders or products
- ❌ Cannot manage system settings

**Dashboard Access:**
- **📊 Main Dashboard** → View statistics
- **📋 Orders List** → All orders, filter by status
- **📈 Reports** → Sales trends, delivery metrics
- **👥 Team** → View staff performance

---

### 3. **Order Entry Operator** 📝
**Permissions:** Create orders, update status

**Features Available:**
- ✅ Create new orders
- ✅ View and update order status
- ✅ Add notes to orders
- ✅ Upload order images
- ❌ Cannot delete orders
- ❌ Cannot view other users' data
- ❌ Cannot access reports

**Dashboard Access:**
- **📊 Quick Stats** → Today's orders only
- **➕ Create Order** → POS entry form
- **📋 My Orders** → Orders created by this user
- **🏷️ Scan Barcode** → Quick order lookup

---

### 4. **Warehouse Staff** 📦
**Permissions:** Update order status, scan barcodes

**Features Available:**
- ✅ View assigned orders
- ✅ Update status (processing → packed → shipped)
- ✅ Scan barcodes
- ✅ Upload images (delivery proof)
- ❌ Cannot create orders
- ❌ Cannot modify products
- ❌ Cannot delete anything

**Dashboard Access:**
- **📊 My Queue** → Orders assigned to me
- **🏷️ Scan & Track** → Barcode scanner interface
- **📸 Add Proof** → Upload delivery photos

---

## 🗺️ Navigation Map

### ALL ROLES START HERE:
```
🎫 DISTRODOG POS
├── Dashboard        → Statistics & quick actions
├── Orders          → List with role-based visibility
├── Create Order    → (Operator+ only)
├── Scan Barcode    → Quick lookup
└── Logout
```

### Role-Based Navigation

**ADMIN:**
```
Dashboard
├── Admin Panel
│   ├── Users Management
│   ├── Products
│   ├── Orders (All)
│   └── Audit Logs
├── Reports
│   ├── Sales Report
│   ├── Delivery Metrics
│   └── Staff Performance
└── Settings
```

**MANAGER:**
```
Dashboard
├── Team Overview
├── All Orders
├── Reports
│   ├── Sales
│   └── Delivery Status
└── Staff View
```

**OPERATOR:**
```
Dashboard
├── Create Order
├── My Orders
├── Scan Barcode
└── Today's Statistics
```

**WAREHOUSE:**
```
Dashboard
├── My Queue (Assigned)
├── Scan & Update Status
└── Upload Proof
```

---

## 📋 Common Tasks by Role

### Operator: Create a New Order

1. Click **"Create Order"** from dashboard
2. Fill in:
   - Customer Name
   - Product (select from dropdown)
   - Quantity
   - Barcode (optional - auto-generated if empty)
   - Notes (optional)
3. Click **"Create Order"**
4. Order appears in "My Orders" and dashboard recent list

### Manager: View Order Status Report

1. Go to **Dashboard** → **Reports**
2. Select **"Delivery Status"**
3. Filter by date range or product
4. View statistics:
   - New orders
   - Processing
   - Packed
   - Shipped
   - Delivered

### Warehouse Staff: Complete Order via Barcode

1. Go to **Scan & Track**
2. Scan barcode (or type if manual)
3. View order details
4. Update status:
   - "Packed" → ready for shipment
   - "Shipped" → sent out
5. Upload delivery proof (photo)
6. Click "Mark Complete"

### Admin: Add New User

1. Go to **Admin Panel** → **Users Management**
2. Click **"Add User"**
3. Fill in:
   - Username
   - Email
   - Role (select from dropdown)
   - Password
4. Click **"Create"**
5. User can now login

---

## 🔐 Login & Permissions

### First Login (Admin Setup)

```bash
# Admin credentials (set during initial setup)
Username: root
Password: root  (change this!)

# Access
http://localhost:8000/admin/
```

### Set User Roles (Admin Only)

1. Login as Admin
2. Go to Django Admin → Users
3. Select user
4. In **Groups** section, select role:
   - managers
   - operators
   - warehouse_staff
5. Click **"Save"**

---

## 📱 Dashboard Features by Role

### Statistics Cards (Top of Dashboard)

**Admin/Manager See:**
- Total Orders (system-wide)
- Orders Today
- Pending Orders
- Products Count

**Operator Sees:**
- My Orders (created by me)
- Orders Today (created by me)
- My Pending (status: new/processing)
- Products Available

### Recent Orders Table

**Columns Visible:**
- Order ID
- Customer
- Product
- Quantity
- Status (badge: new=blue, processing=yellow, delivered=green)
- Barcode
- Action (View button)

---

## 🎨 Status Colors & Meanings

```
🔵 NEW          → Just created, not started
🟡 PROCESSING   → Being picked/packed
⚪ PACKED       → Ready to ship
🟣 SHIPPED      → Left warehouse
🟢 DELIVERED    → Received by customer
🔴 CANCELLED    → Order voided
```

---

## 🐛 Troubleshooting

### "Page not accessible for your role"
→ You don't have permission for this feature
→ Contact admin or your manager
→ Check your user role in Admin Panel

### "Order not found when scanning"
→ Check barcode is correct
→ Order may be from different date
→ Ask manager to look up manually

### "Can't create order"
→ Check you have Operator role or higher
→ At least one product must exist
→ Try admin panel: /admin/orders/order/add/

### "Reports not showing data"
→ Select correct date range
→ Make sure orders exist in that period
→ Try exporting as CSV

---

## 📞 Support

**For system issues:** Contact IT/Admin
**For product setup:** Contact Manager
**For order issues:** Contact Warehouse Team Lead

---

## 🔄 System Overview

```
Order Workflow:
New → Processing → Packed → Shipped → Delivered
                 ↓
          (Upload proof photo)
```

**Audit Trail:** Every action logged (who, what, when)
**Backups:** Daily at midnight
**Support:** 24/7 system monitoring

