# Use a lightweight Python base image
FROM python:3.12-slim-bullseye

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install system-level dependencies for Python libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy and install application dependencies first for Docker caching
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire application code
COPY . /app

# Expose the port Flask will run on
EXPOSE 5000

# Set environment variables for Flask
# Replace these with your production values or use Railway's environment configuration
ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Run the Flask app through Gunicorn with create_app()
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]