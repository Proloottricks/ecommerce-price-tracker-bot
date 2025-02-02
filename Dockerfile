# Use official Python image from Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the credentials file into the container
COPY credentials.json /app/credentials.json

# Install any dependencies in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port (if needed)
EXPOSE 5000

# Run the bot when the container launches
CMD ["python", "main.py"]