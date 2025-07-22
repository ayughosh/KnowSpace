# Use official lightweight Python image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy project files into the container
COPY . .

# Install system dependencies (you can modify as needed)
RUN apt-get update && \
    apt-get install -y curl gcc libpq-dev ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your Flask app will run on inside the container
EXPOSE 5000

# Start your Flask app using Gunicorn, pointing to wsgi.py's app object
CMD ["/bin/sh", "-c", "until curl -s http://ollama:11434; do echo 'Waiting for Ollama...'; sleep 2; done && gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app"]
