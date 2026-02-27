FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ind \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create directories
RUN mkdir -p ~/dibs1/{uploads,videos,thumbnails,knowledge,temp}

# Expose port
EXPOSE 8080

# Run
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
