# Verwende ein ARM64-kompatibles Python-Image für Raspberry Pi 4 (64-Bit)
FROM --platform=linux/arm64/v8 arm64v8/python:3.13-slim


# Installiere Systemabhängigkeiten
RUN apt-get update && apt-get install -y \
    python3-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Installiere die Python-Bibliotheken aus der requirements.txt
WORKDIR /app

# Kopiere Dateien in das Image
COPY app/ /app/

# Installiere Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Führe das Skript aus
CMD ["python", "send_mqtt.py"]
