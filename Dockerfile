# Use a lightweight Python image
FROM python:3.12-slim-bullseye

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install system-level dependencies
# These are necessary for Python packages like Pillow (image processing) and psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker's caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the entire Flask project into the container
COPY . /app

# Expose the port used by Flask
EXPOSE 5000

# Set the environment variables (adjust as needed or configure in Railway)
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run using Gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]