# Basis-Image mit Python
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    python3-rpi.gpio \
    && rm -rf /var/lib/apt/lists/*

# Setze Arbeitsverzeichnis
WORKDIR /app

# Kopiere Dateien in das Image
COPY app/ /app/

# Installiere Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Standardkommando: MQTT-Sender starten
CMD ["python", "send_mqtt.py"]

