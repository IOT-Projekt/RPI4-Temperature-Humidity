# Verwende ein ARM64-kompatibles Python-Image für Raspberry Pi 4 (64-Bit)
FROM arm64v8/python:3.9-bookworm


# Installiere Systemabhängigkeiten
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Installiere die Python-Bibliotheken aus der requirements.txt
COPY requirements.txt /tmp/
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Kopiere den Rest der Anwendung (deine Skripte)
COPY . /app/
WORKDIR /app

# Startbefehl für das Python-Skript
CMD ["python", "send_mqtt.py"]
