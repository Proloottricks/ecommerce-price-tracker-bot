FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy all files to the container
COPY . /app

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (if needed)
EXPOSE 5000

# Set the entry point for the application
CMD ["python", "main.py"]