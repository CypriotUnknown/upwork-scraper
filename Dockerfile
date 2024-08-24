# Use the smallest Python image with a slim Debian base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install dependencies
# The `--no-cache-dir` option avoids caching the package index
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy the application requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Specify the command to run on container start
CMD ["python3", "main.py"]