# DistRodog - Django ERP Setup Guide

## Quick Start with Docker (Recommended)

### Prerequisites
- Git
- Docker & Docker Compose
- ~5 minutes of setup time

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/sudo29/distrodog.git
cd distrodog

# 2. Start containers
docker-compose up --build

# 3. In another terminal, create superuser
docker-compose exec web python manage.py createsuperuser

# 4. Access the application
# Admin: http://localhost:8000/admin
# API: http://localhost:8000/api/
```

## Manual Setup (Without Docker)

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Git

### Installation Steps

```bash
# 1. Clone and navigate
git clone https://github.com/sudo29/distrodog.git
cd distrodog

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Run development server
python manage.py runserver
```

## Deployment to Fly.io

### Prerequisites
- Fly.io account (free tier available)
- Flyctl CLI installed

### Deployment Steps

```bash
# 1. Login to Fly.io
flyctl auth login

# 2. Create app
flyctl launch --name distrodog --region sin  # Singapore region for best Thailand performance

# 3. Set secrets
flyctl secrets set SECRET_KEY="your-django-secret-key"
flyctl secrets set DEBUG=False

# 4. Deploy
git push origin main  # Trigger automatic deployment

# 5. Create superuser
flyctl ssh console
python manage.py createsuperuser
exit

# 6. Access application
# Your app URL will be shown after deployment
```

## Key Features

- **Orders Management**: Track orders from new → processing → packed → shipped → delivered
- **Product Inventory**: Manage products, SKUs, barcodes, and quantities
- **Barcode Scanning**: Support for barcode readers and QR codes
- **Image Attachments**: Attach photos to orders for documentation
- **Scan Logging**: Complete audit trail of all scans and actions
- **Django Admin**: Clean, user-friendly management interface
- **PostgreSQL Database**: Reliable, scalable database
- **Docker Support**: Easy containerization for any environment

## Database Models

### Product
- `name`: Product name (CharField)
- `sku`: Unique SKU (CharField, unique)
- `barcode`: Barcode/QR code value (CharField)
- `quantity`: Current stock quantity (PositiveIntegerField)
- `description`: Product details (TextField)
- `created_at`, `updated_at`: Timestamps (DateTimeField)

### Order
- `customer`: Customer name (CharField)
- `product`: Foreign key to Product
- `quantity`: Ordered quantity (PositiveIntegerField)
- `status`: Order status - new, processing, packed, shipped, delivered, cancelled
- `barcode`: Order tracking barcode (CharField)
- `notes`: Order-specific notes (TextField)
- `created_by`: User who created order (ForeignKey)
- `created_at`, `updated_at`: Timestamps

### ImageAttachment
- `order`: Foreign key to Order
- `image`: Image file (ImageField)
- `uploaded_by`: User who uploaded (ForeignKey)
- `uploaded_at`: Timestamp (DateTimeField)

### ScanLog
- `order`: Foreign key to Order
- `barcode_data`: Scanned barcode value (CharField)
- `action`: Action type (CharField) - received, packed, shipped
- `scanned_by`: User who scanned (ForeignKey)
- `scanned_at`: Timestamp (DateTimeField)

## Environment Variables (.env)

```
DEBUG=True  # Set to False in production
SECRET_KEY=your-secret-key-here
DB_NAME=distrodog
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost  # Use 'db' in Docker
DB_PORT=5432
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

## Common Commands

```bash
# Create new database migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Collect static files
python manage.py collectstatic

# Open Django shell
python manage.py shell

# Run tests
python manage.py test
```

## Troubleshooting

### PostgreSQL Connection Error
- Ensure PostgreSQL is running
- Check DB credentials in .env
- Verify database name matches

### Port Already in Use
```bash
# Change port
python manage.py runserver 8001
# Or for Docker
docker-compose down  # Stop containers
docker-compose up  # Restart
```

### Static Files Not Loading
```bash
python manage.py collectstatic --clear --noinput
```

## Support & Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Admin Documentation](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Fly.io Documentation](https://fly.io/docs/)
- [Docker Documentation](https://docs.docker.com/)

## License

MIT License - Feel free to use, modify, and distribute

## Contributors

DistRodog is an open-source project. Contributions are welcome!
