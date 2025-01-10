# Basis-Image mit Python
FROM python:3.9-slim

# Setze Arbeitsverzeichnis
WORKDIR /app

# Kopiere Dateien in das Image
COPY app/ /app/

# Installiere Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Standardkommando: MQTT-Sender starten
CMD ["python", "send_mqtt.py"]
