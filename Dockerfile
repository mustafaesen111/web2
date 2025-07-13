# Python tabanlı image
FROM python:3.10

# Çalışma dizini
WORKDIR /app

# Gereksinim dosyaları kopyalanır
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyaları kopyalanır
COPY . .

# Ortam değişkenleri için .env kullanılacaksa
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Flask başlat
CMD ["flask", "run"]
