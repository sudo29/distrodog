# distrodog

## POS Order Management System (distrodog/orders)

A complete Django-based Point of Sale (POS) order management system with barcode scanning, inventory tracking, and complete audit trail.

### Features

✅ **Complete Data Models:**
- **Products**: SKU/barcode management with inventory tracking
- **Orders**: Full order lifecycle (new → processing → packed → shipped → delivered → cancelled)
- **Image Attachments**: Upload and attach photos/documentation to orders
- **Scan Logs**: Complete audit trail of all scans and status changes

✅ **POS Management Views:**
- Dashboard with order statistics
- Order list with filtering and search
- Create new orders (POS-style entry)
- Order detail view with image gallery
- Barcode scanning interface
- Order status tracking

✅ **Hardware Integration Ready:**
- USB barcode scanner support
- Camera/image capture for documentation
- Audit logging for compliance

✅ **Django Admin Interface:**
- Full admin panel for Products, Orders, Images, and Scan Logs
- Advanced filtering and search
- Read-only audit trail protection

### Quick Start

```bash
# Initialize database
docker-compose up --build
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Access interfaces
Admin Panel:        http://localhost:8000/admin/
POS Dashboard:      http://localhost:8000/pos/
Order Management:   http://localhost:8000/pos/orders/
Create Order:       http://localhost:8000/pos/orders/create/
Barcode Scan:       http://localhost:8000/pos/scan/
```

See `orders/DB_SETUP.md` for detailed database setup and troubleshooting.
