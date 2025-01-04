FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your Python script
COPY scripts/ /app

# Set the default command to run
CMD ["python", "/app/srv.py"]
