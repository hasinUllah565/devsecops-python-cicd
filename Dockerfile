
# Use Python 3.10
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ ./app/
COPY config.py run.py ./

# Set Flask environment
ENV HOST=0.0.0.0
ENV PORT=5000
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1

# Application port
EXPOSE 5000

# Start Flask application
CMD ["python", "run.py"]
