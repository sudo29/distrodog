# Database Setup Guide for Distrodog ERP

## Database Migration Commands

Run these commands in your Docker container to initialize the database:

```bash
# Create migrations for all model changes
docker-compose exec web python manage.py makemigrations

# Apply all migrations to the database
docker-compose exec web python manage.py migrate

# Restart the web container
docker-compose restart web
```

## Verify Installation

After running migrations, verify the database was created:

1. Navigate to: `http://localhost:8000/admin/`
2. Log in with your superuser credentials (root/root)
3. You should see in the left sidebar:
   - **ORDERS** section with:
     - Products
     - Orders
     - Image Attachments
     - Scan Logs

## Access the POS Management System

After admin verification, access the POS interface:

- **Dashboard**: `http://localhost:8000/pos/`
- **Orders List**: `http://localhost:8000/pos/orders/`
- **Create Order**: `http://localhost:8000/pos/orders/create/`
- **Barcode Scan**: `http://localhost:8000/pos/scan/`

## Database Tables Created

### orders_product
- name: VARCHAR(255)
- sku: VARCHAR(100) - UNIQUE
- barcode: VARCHAR(255) - UNIQUE
- description: TEXT
- quantity: INTEGER
- created_at, updated_at: TIMESTAMP

### orders_order
- customer: VARCHAR(255)
- product_id: FOREIGN KEY to orders_product
- quantity: INTEGER
- status: CHOICE (new, processing, packed, shipped, delivered, cancelled)
- barcode: VARCHAR(255) - UNIQUE
- notes: TEXT
- created_by_id: FOREIGN KEY to auth_user
- created_at, updated_at: TIMESTAMP

### orders_imageattachment
- order_id: FOREIGN KEY to orders_order
- image: ImageField
- uploaded_by_id: FOREIGN KEY to auth_user
- uploaded_at: TIMESTAMP

### orders_scanlog
- order_id: FOREIGN KEY to orders_order
- barcode_data: VARCHAR(255)
- scanned_by_id: FOREIGN KEY to auth_user
- action: CHOICE (scan, status_change, image_upload, note_added, order_created)
- scanned_at: TIMESTAMP (auto-created)
- details: JSON

## Troubleshooting

If you encounter "table doesn't exist" errors:

1. Check migrations were applied: `docker-compose exec web python manage.py showmigrations orders`
2. If migrations show as unapplied, run: `docker-compose exec web python manage.py migrate orders`
3. If database is corrupted, remove the Docker volume and restart

## Full System Initialization

```bash
# Build and start containers
docker-compose up --build

# Create superuser (if not already created)
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Restart web container
docker-compose restart web

# Verify by accessing http://localhost:8000/admin/
```

The system is now ready for order management!
