import os
import time
import paho.mqtt.client as mqtt
from read_sensor import read_sensor
import json

# Konstanten und Standardwerte
DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 1883
DEFAULT_TOPIC_TEMPERATURES = "iot/devices/temperatures"
DEFAULT_TOPIC_HUMIDITY = "iot/devices/humidity"
DEFAULT_USERNAME = None
DEFAULT_PASSWORD = None
SEND_MQTT_INTERVAL = 10

# Umgebungsvariablen
BROKER = os.getenv("BROKER_IP", DEFAULT_BROKER)
PORT = int(os.getenv("BROKER_PORT", DEFAULT_PORT))
TOPIC_TEMPERATURES = os.getenv("TOPIC_TEMPERATURES", DEFAULT_TOPIC_TEMPERATURES)
TOPIC_HUMIDITY = os.getenv("TOPIC_HUMIDITY", DEFAULT_TOPIC_HUMIDITY)
MQTT_USERNAME = os.getenv("MQTT_USERNAME", DEFAULT_USERNAME)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", DEFAULT_PASSWORD)
CLIENT_ID = os.getenv("CLIENT_ID", "dht22-sensor")

# Initialisiere MQTT-Client
client = mqtt.Client()

# Authentifizierung hinzufügen
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Callback-Funktionen für Debugging
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Verbunden mit dem Broker")
    else:
        print(f"Verbindung fehlgeschlagen. Code: {rc}")

def on_publish(client, userdata, mid):
    print(f"Nachricht mit ID {mid} veröffentlicht")


client.on_connect = on_connect
client.on_publish = on_publish

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
    print(f"Some env: {TOPIC_HUMIDITY}, -> {humidity_payload}")
    print(f"Feuchtigkeit gesendet: {humidity_payload}")
    
    # Sende Temperaturdaten
    temperature_payload = json.dumps({
        "source" : "mqtt",
        "device_id" : CLIENT_ID,
        "temperature_c": data["temperature_c"],
        "timestamp": data["timestamp"]
    })
    client.publish(TOPIC_TEMPERATURES, temperature_payload)
    print(f"Temperaturen gesendet: {temperature_payload}")

if __name__ == "__main__":
    client.loop_start()  # Startet die MQTT-Netzwerkkommunikation im Hintergrund

    while True:
        sensor_data = read_sensor()
        if sensor_data:  # Sicherstellen, dass Sensordaten nicht `None` sind
            send_mqtt(sensor_data)
        time.sleep(SEND_MQTT_INTERVAL)