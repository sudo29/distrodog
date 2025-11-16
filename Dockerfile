# Use official Python 3.9 slim image (lightweight, includes only essentials)
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies needed for PostgreSQL and Pillow (image processing)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

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
# Note: manage.py is in root directory
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
