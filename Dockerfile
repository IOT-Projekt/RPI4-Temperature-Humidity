# Verwende ein ARM-kompatibles Python-Image (z.B. für Raspberry Pi)
FROM python:3.9-slim

# Installiere RPi.GPIO und andere Abhängigkeiten

# Installiere Python-Abhängigkeiten
COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Kopiere deine App
COPY . /app/
WORKDIR /app

# Startbefehl für das Python-Skript
CMD ["python", "send_mqtt.py"]
