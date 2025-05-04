FROM python:3.11-slim

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Set working directory
WORKDIR /app

# Copy all files to the container
COPY . .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Start the bot (replace with your main file if needed)
CMD ["python", "main.py"]
