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

# Copy dependency file requirements first to leverage caching
COPY requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the entire application code
COPY . /app

# Expose the port Flask will run on
EXPOSE 5000

# Run the Flask app through Gunicorn with create_app()
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app.__init__:create_app()"]