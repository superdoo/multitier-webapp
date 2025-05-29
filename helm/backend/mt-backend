FROM python:3.10-slim

ARG CACHEBUST=1


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install curl
RUN apt-get update && apt-get install -y curl && apt-get clean

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
