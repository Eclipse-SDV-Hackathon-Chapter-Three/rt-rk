FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install \
    git \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy and install requirements
COPY requirements.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt

# Copy emergency worker code
COPY . ./

# Set the Python path
ENV PYTHONPATH="/usr/src/app:${PYTHONPATH}"

# Run the emergency worker
CMD ["python", "worker_emergency.py"]