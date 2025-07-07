FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8001", "app:server"]
