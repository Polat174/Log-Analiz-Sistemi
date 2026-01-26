FROM python:3.10-slim

WORKDIR /app

COPY gereksinimler.txt .
RUN pip install --no-cache-dir -r gereksinimler.txt

COPY . .

RUN mkdir -p /var/log/host_logs

CMD ["python", "main.py"]
