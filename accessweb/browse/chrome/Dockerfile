FROM python:3.10

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY script.py /app/script.py
COPY logger_config.py /app/logger_config.py

FROM python:3.10

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY script.py logger_config.py ./

# Install system dependencies
RUN apt-get update && \
    apt-get install -y wget unzip tesseract-ocr && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["python", "script.py"]