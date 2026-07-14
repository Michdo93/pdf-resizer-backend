FROM python:3.12-slim

# Verhindert, dass Python pyc-Dateien schreibt und puffert
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY app.py .

# Render setzt die PORT-Variable automatisch. Wir nutzen sie als Standardwert.
EXPOSE 8080
ENV PORT=8080

# Gunicorn starten und an den Port binden
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "app:app"]
