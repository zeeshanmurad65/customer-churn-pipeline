FROM python:3.10-slim

WORKDIR /app

# Install dependencies first to cache this layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your database.py, load_data.py, and the model folder
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Start the server using your specific load_data.py file
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]