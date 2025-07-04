FROM python:3.12

WORKDIR /app

COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8001

CMD ["gunicorn", "--worker=1", "--threads=8", "--bind" "0.0.0.0:8001", "main:server"]
