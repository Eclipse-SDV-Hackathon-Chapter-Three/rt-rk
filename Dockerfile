FROM python:3.12-slim-bookworm as base

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install \
    git \
    # you can add other dependencies here
    # ..
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY workers/ ./workers/

# Run the supervisor by default (this image will be used by workloads)
CMD [ "python", "-u", "./supervisor.py" ]