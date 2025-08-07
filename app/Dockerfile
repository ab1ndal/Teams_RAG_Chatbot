# app/Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies using uv or pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose port for Railway
EXPOSE 8080

# Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
