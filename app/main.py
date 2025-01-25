import os
import time
import paho.mqtt.client as mqtt
from read_sensor import read_sensor
import json
import logging
import threading

# Create a lock for thread-safe operations
lock = threading.Lock()

# setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# sending interval in seconds, default is 10 seconds
send_message_interval = 10

# Umgebungsvariablen
BROKER = os.getenv("BROKER_IP", "localhost")
PORT = int(os.getenv("BROKER_PORT", 1883))
TOPIC_TEMPERATURES = os.getenv("TOPIC_TEMPERATURES", "iot/devices/temperatures")
TOPIC_HUMIDITY = os.getenv("TOPIC_HUMIDITY", "iot/devices/humidity")
TOPIC_FREQUENCY = os.getenv("TOPIC_FREQUENCY", "iot/devices/frequency")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", None)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", None)
CLIENT_ID = os.getenv("CLIENT_ID", "dht22-sensor")

# Initialisiere MQTT-Client
client = mqtt.Client()

# Authentifizierung hinzufügen
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)


# Callback-Funktionen für Connection logging
def on_connect(client, userdata, flags, rc):
    # Wenn die Verbindung erfolgreich ist, wird das Topic Frequenz abonniert
    if rc == 0:
        logging.info("Verbunden mit dem Broker")
        client.subscribe(TOPIC_FREQUENCY)
        logging.info(f"Abonniere {TOPIC_FREQUENCY}")  # Info Meldung loggen
    else:
        logging.error(f"Verbindung fehlgeschlagen. Code: {rc}")


# Callback-Funktionen für Publish logging
def on_publish(client, userdata, mid):
    logging.info(f"Nachricht mit ID {mid} veröffentlicht")


# Callback-Funktionen für Message logging
def on_message(client, userdata, message):
    logging.info(f"Nachricht empfangen: {message.payload.decode()}")

    # Falls es sich um eine Frequenznachricht handelt, wird die Sendefrequenz aktualisiert
    if message.topic == TOPIC_FREQUENCY:
        # Lock setzen, um sicherzustellen, dass die Sendefrequenz nicht gleichzeitg im main Thread gelesen wird
        with lock:
            global send_message_interval

            # Frequenzwert aus der Nachricht extrahieren und Variable updaten
            payload = json.loads(message.payload.decode())["payload"]
            send_message_interval = int(payload["frequency"])

            logging.info(f"Send interval changed to {send_message_interval} seconds")


# Callback Funktionen setzen
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# Verbinden mit dem Broker
client.connect(BROKER, PORT, keepalive=60)


def send_mqtt(data):
    """Sendet Humdity, Temperatur und Zeitstempel an den MQTT-Broker."""
    # Wenn keine Daten vorhanden sind, wird die Funktion beendet
    if data is None:
        return

    # Humdity Payload erstellen und an MQTT Broker senden
    humidity_payload = json.dumps(
        {
            "source": "mqtt",
            "device_id": CLIENT_ID,
            "humidity": data["humidity"],
            "timestamp": data["timestamp"],
        }
    )
    client.publish(TOPIC_HUMIDITY, humidity_payload)
    logging.info(f"Feuchtigkeit gesendet: {humidity_payload}")

    # Temperature Payload erstellen und an MQTT Broker senden
    temperature_payload = json.dumps(
        {
            "source": "mqtt",
            "device_id": CLIENT_ID,
            "temperature_c": data["temperature_c"],
            "timestamp": data["timestamp"],
        }
    )
    client.publish(TOPIC_TEMPERATURES, temperature_payload)
    logging.info(f"Temperaturen gesendet: {temperature_payload}")


if __name__ == "__main__":
    # Startet die MQTT-Loop in einem eigenen Thread. Nachrichten zur Frequenzänderung werden somit in einem eigenen Thread verarbeitet
    client.loop_start()

    # Sensordaten in einer Endlosschleife einlesen, dem Broker senden und nach einer bestimmten Pause wiederholen
    while True:
        sensor_data = read_sensor()
        if sensor_data:  # Sicherstellen, dass auch Sensorwerte vorhanden sind
            send_mqtt(sensor_data)

        # Lock setzen, um sicherzustellen, dass die Sendefrequenz nicht gleichzeitg im anderen Thread geändert wird
        with lock:
            time.sleep(send_message_interval)
