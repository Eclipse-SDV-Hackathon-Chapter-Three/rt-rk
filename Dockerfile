FROM python:3.12-slim-bookworm as base

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --force-reinstall --no-cache-dir opencv-python-headless==4.12.0.88
RUN pip install --no-cache-dir -r requirements.txt
COPY workers/ ./workers/

# Run the supervisor by default (this image will be used by workloads)
CMD [ "python", "-u", "./supervisor.py" ]