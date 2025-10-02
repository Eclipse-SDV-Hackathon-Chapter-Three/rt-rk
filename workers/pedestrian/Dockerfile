# Use Python slim base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app


RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the default Zenoh port (optional, for documentation)
EXPOSE 7447

# Set the entrypoint to run the simple zenoh publisher
ENTRYPOINT ["python", "worker_pedestrian.py"]
