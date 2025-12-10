# CrewAI Tool Index Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create data directories
RUN mkdir -p /app/data/tools \
    /app/data/components \
    /app/data/chromadb

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8086

# Expose port
EXPOSE 8086

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8086/api/crewai/tool-index/health')"

# Run the service
CMD ["python", "src/service.py"]
