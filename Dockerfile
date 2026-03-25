
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential
RUN apt install -y libpq-dev
RUN pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV ENVIRONMENT=production
EXPOSE 8000
RUN chmod +x start.sh

# Command to run the app
# CMD ["python", "main.py"]
CMD ["./start.sh"]