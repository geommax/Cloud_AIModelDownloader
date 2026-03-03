FROM python:3.12-slim

LABEL maintainer="mr_cobot"
LABEL description="Hugging Face Model Downloader CLI"

# System dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/hfdl/venv
ENV PATH="/opt/hfdl/venv/bin:$PATH"

# Install Python dependencies
COPY app/requirements.txt /opt/hfdl/requirements.txt
RUN pip install --no-cache-dir -r /opt/hfdl/requirements.txt

# Copy CLI app
COPY app/cli.py /opt/hfdl/cli.py

# Install CLI as a command
RUN printf '#!/bin/bash\npython /opt/hfdl/cli.py "$@"\n' > /usr/local/bin/hfdl && \
    chmod +x /usr/local/bin/hfdl

# Create models directory (mount point)
RUN mkdir -p /models /tmp/hf_cache
VOLUME /models

ENV HF_DOWNLOAD_DIR=/models
ENV HF_HOME=/models

# Entrypoint
COPY entrypoint.sh /opt/hfdl/entrypoint.sh
RUN chmod +x /opt/hfdl/entrypoint.sh

# Create non-root user (uid 1000) and set permissions
RUN groupadd -g 1000 hfdl && \
    useradd -u 1000 -g 1000 -m hfdl && \
    chown -R 1000:1000 /models /opt/hfdl /tmp/hf_cache

WORKDIR /models
USER 1000:1000
ENTRYPOINT ["/opt/hfdl/entrypoint.sh"]
