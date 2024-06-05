FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev libssl-dev && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8000
CMD ["python", "./app.py"]
