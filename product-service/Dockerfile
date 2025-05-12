FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make the entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Use the entrypoint script
ENTRYPOINT ["./docker-entrypoint.sh"]
