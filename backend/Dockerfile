# Use a lightweight official Python image
FROM python:3.10-slim

# Prevent Python from writing .pyc files and force stdout logging (good for live streams!)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (to leverage Docker caching)
COPY requirements.txt .

# Install the Python dependencies (FastAPI, LangGraph, GenAI, Docker SDK, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code into the container
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]