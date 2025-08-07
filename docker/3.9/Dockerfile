FROM python:3.9-slim

WORKDIR /pure_core

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Εγκαθιστούμε και το pytest αν δεν είναι στο requirements.txt
RUN pip install pytest
COPY . .

CMD ["pytest"]
