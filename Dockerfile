# Use a minimal Python image
FROM python:3.12-slim-bullseye

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install system dependencies for Python libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    gcc \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy only the requirements file initially (to leverage Docker layer caching)
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire project into the container
COPY . /app

# Expose Flask's port
EXPOSE 5000

# Use Gunicorn to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "website:create_app()"]