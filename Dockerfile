# Use an official Python image
FROM python:3.12-slim-bullseye

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Set the working directory inside the container
WORKDIR /app

# Copy requirement files and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /app

# Expose the port that Railway provides
EXPOSE 5000

# Start Gunicorn for production
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app.website:create_app"]