# Use official Python 3.9 slim image (lightweight, includes only essentials)
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for PostgreSQL and Pillow (image processing)
RUN apt-get update && apt-get install -y \
    postgresql-client \  # For database operations
    libpq-dev \         # PostgreSQL development headers
    gcc \               # C compiler for some Python packages
    libjpeg-dev \       # JPEG support for Pillow
    zlib1g-dev \        # PNG support for Pillow
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . .

# Create media directory for user uploads (images, documents)
RUN mkdir -p /app/media

# Expose port 8000 for Django development server
EXPOSE 8000

# Default command (overridden in docker-compose.yml)
# Note: manage.py is in distrodog/manage.py subdirectory
CMD ["python", "distrodog/manage.py", "runserver", "0.0.0.0:8000"]
