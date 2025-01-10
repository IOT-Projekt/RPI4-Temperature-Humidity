import time
import paho.mqtt.client as mqtt
from read_sensor import read_sensor

# MQTT-Einstellungen
MQTT_BROKER = "mosquitto.elephant-ladon.ts.net"
MQTT_PORT = 1883  # Standardport für unverschlüsseltes MQTT
MQTT_TOPIC = "iot/devices/temperatures"
MQTT_CLIENT_ID = "DHT22_Sensor"

# Constants and defaults
DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 1883
DEFAULT_TOPIC = "TOPIC NOT FOUND"
CLIENT_ID_PREFIX = "fake-temp-device-"

# Environment variables
BROKER = os.getenv("BROKER_IP", DEFAULT_BROKER)
PORT = int(os.getenv("BROKER_PORT", DEFAULT_PORT))
TOPIC = os.getenv("TOPIC", DEFAULT_TOPIC)
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "your_username")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "your_password")

# Initialisiere MQTT-Client
client = mqtt.Client(MQTT_CLIENT_ID)
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

def send_mqtt(data):
    """Sendet Daten an den MQTT-Broker."""
    if data:
        client.publish(MQTT_TOPIC, str(data))
        print(f"Daten gesendet: {data}")

if __name__ == "__main__":
    while True:
        sensor_data = read_sensor()
        send_mqtt(sensor_data)
        time.sleep(2.0)

