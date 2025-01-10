import os
import time
import paho.mqtt.client as mqtt
from read_sensor import read_sensor

# Konstanten und Standardwerte
DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 1883
DEFAULT_TOPIC_TEMPERATURES = "iot/devices/temperatures"
DEFAULT_TOPIC_HUMIDITY = "iot/devices/humidity"
DEFAULT_USERNAME = None
DEFAULT_PASSWORD = None

# Umgebungsvariablen
BROKER = os.getenv("BROKER_IP", DEFAULT_BROKER)
PORT = int(os.getenv("BROKER_PORT",str(DEFAULT_PORT)))
TOPIC_TEMPERATURES = os.getenv("TOPIC_TEMPERATURES", DEFAULT_TOPIC_TEMPERATURES)
TOPIC_HUMIDITY = os.getenv("TOPIC_HUMIDITY", DEFAULT_TOPIC_HUMIDITY)
MQTT_USERNAME = os.getenv("MQTT_USERNAME", DEFAULT_USERNAME)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", DEFAULT_PASSWORD)

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
    if data:
        # Sende Temperaturdaten
        temperature_payload = {
            "temperature_c": data["temperature_c"],
            "temperature_f": data["temperature_f"],
        }
        client.publish(TOPIC_TEMPERATURES, str(temperature_payload))
        print(f"Temperaturen gesendet: {temperature_payload}")

        # Sende Feuchtigkeitsdaten
        humidity_payload = {"humidity": data["humidity"]}
        client.publish(TOPIC_HUMIDITY, str(humidity_payload))
        print(f"Feuchtigkeit gesendet: {humidity_payload}")

if __name__ == "__main__":
    client.loop_start()  # Startet die MQTT-Netzwerkkommunikation im Hintergrund
    try:
        while True:
            sensor_data = read_sensor()
            if sensor_data:  # Sicherstellen, dass Sensordaten nicht `None` sind
                send_mqtt(sensor_data)
            time.sleep(2.0)
    except KeyboardInterrupt:
        print("Beenden...")
        client.loop_stop()  # Beendet die MQTT-Netzwerkkommunikation
        client.disconnect()
