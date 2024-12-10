# Start from a minimal Python base image
FROM python:3.12-slim-bullseye

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    gcc \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory to the root of your project
WORKDIR /app

# Copy dependencies file first (to leverage caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the whole project into the container
COPY . /app

# Set PYTHONPATH to app/ so the website module can be imported
ENV PYTHONPATH=/app

# Expose the port for Flask
EXPOSE 5000

# Run the application with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "website:create_app()"]