FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY requirements.txt /app/

# Install build deps needed for mysqlclient and common cryptography libs
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    python3-dev \
    libssl-dev \
    libffi-dev \
    ca-certificates \
    curl && \
    pip install --upgrade pip wheel setuptools && \
    pip install -r requirements.txt && \
    apt-get remove -y build-essential python3-dev pkg-config && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
EXPOSE 8000
