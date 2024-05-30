FROM python:3.9-buster

WORKDIR /app

# Update APT packages and install necessary dependencies
RUN apt-get update && \
	apt-get install -y wget gnupg2 && \
	apt-get install -y chromium && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/yt-dlp && \
	chmod a+rx /usr/local/bin/yt-dlp

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p downloads logs

# Run the application
CMD ["python", "run.py"]
