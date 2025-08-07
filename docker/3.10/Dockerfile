FROM python:3.10-slim

WORKDIR /pure_core

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["pytest"]
