# Verwende ein ARM64-kompatibles Python-Image für Raspberry Pi 4 (64-Bit)
FROM python:3.11-slim


RUN apt-get install -y build-essential python3-dev libgpiod2 libmariadb-dev
# Installiere die Python-Bibliotheken aus der requirements.txt
WORKDIR /app

# Kopiere Dateien in das Image
COPY app/ /app/

# Installiere Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Führe das Skript aus
CMD ["python", "send_mqtt.py"]
