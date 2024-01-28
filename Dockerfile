# Use the official Python image as the base image
FROM python:3.9-slim-buster

# Set the working directory inside the container
WORKDIR /app
COPY config/config.json /app/config/config.json


# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory to the container
COPY . .

# Expose the port your Flask app will be listening on
EXPOSE 8081

# Run the Flask app when the container starts
CMD ["python", "wol4.py"]