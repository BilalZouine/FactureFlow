FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 5000

COPY . .

CMD ["python", "run.py"]