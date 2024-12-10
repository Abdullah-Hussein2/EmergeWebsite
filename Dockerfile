# Start with a minimal Python 3.12 base image
FROM python:3.12-slim-bullseye

# Upgrade pip to the latest version
RUN pip install --no-cache-dir --upgrade pip

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the dependencies file first for caching
COPY requirements.txt /app/

# Install Python libraries
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire project into the container
COPY . /app

# Set PYTHONPATH to include the app directory, so Python can find `website` module
ENV PYTHONPATH=/app/app:$PYTHONPATH

# Expose the default Flask port
EXPOSE 5000

# Run the Flask app using Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "website:create_app()"]