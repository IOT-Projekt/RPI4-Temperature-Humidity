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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# sending interval in seconds 
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

# Callback-Funktionen für Debugging
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Verbunden mit dem Broker")
        client.subscribe(TOPIC_FREQUENCY)
        logging.info(f"Abonniere {TOPIC_FREQUENCY}")
    else:
        logging.error(f"Verbindung fehlgeschlagen. Code: {rc}")

def on_publish(client, userdata, mid):
    logging.info(f"Nachricht mit ID {mid} veröffentlicht")

def on_message(client, userdata, message):
    logging.info(f"Nachricht empfangen: {message.payload.decode()}")
    if message.topic == TOPIC_FREQUENCY:
        with lock:
            global send_message_interval
            payload = json.loads(message.payload.decode())["payload"]
            send_message_interval = int(payload["frequency"])
            logging.info(f"Send interval changed to {send_message_interval} seconds")

client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# Verbinden mit dem Broker
client.connect(BROKER, PORT, keepalive=60)

def send_mqtt(data):
    """Sendet Daten an den MQTT-Broker."""
    if data is None: 
        return

    # Sende Feuchtigkeitsdaten
    humidity_payload = json.dumps({
        "source" : "mqtt",
        "device_id" : CLIENT_ID,
        "humidity": data["humidity"],
        "timestamp": data["timestamp"]
    })        
    client.publish(TOPIC_HUMIDITY, humidity_payload)
    logging.info(f"Feuchtigkeit gesendet: {humidity_payload}")
    
    # Sende Temperaturdaten
    temperature_payload = json.dumps({
        "source" : "mqtt",
        "device_id" : CLIENT_ID,
        "temperature_c": data["temperature_c"],
        "timestamp": data["timestamp"]
    })
    client.publish(TOPIC_TEMPERATURES, temperature_payload)
    logging.info(f"Temperaturen gesendet: {temperature_payload}")


if __name__ == "__main__":
    client.loop_start()  # Startet die MQTT-Netzwerkkommunikation im Hintergrund

    while True:
        sensor_data = read_sensor()
        if sensor_data:  # Sicherstellen, dass Sensordaten nicht `None` sind
            send_mqtt(sensor_data)
        with lock:
            time.sleep(send_message_interval)
