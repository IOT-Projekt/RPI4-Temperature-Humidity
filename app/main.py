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

# Constants based on environment variables
BROKER = os.getenv("BROKER_IP", "localhost")
PORT = int(os.getenv("BROKER_PORT", 1883))
TOPIC_TEMPERATURES = os.getenv("TOPIC_TEMPERATURES", "iot/devices/temperatures")
TOPIC_HUMIDITY = os.getenv("TOPIC_HUMIDITY", "iot/devices/humidity")
TOPIC_FREQUENCY = os.getenv("TOPIC_FREQUENCY", "iot/devices/frequency")
MQTT_USERNAME = os.getenv("MQTT_USERNAME", None)
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", None)
CLIENT_ID = os.getenv("CLIENT_ID", "dht22-sensor")

# Initialize the MQTT client
client = mqtt.Client()

# If username and password are set, use them for authentication
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)


# Callback function for connection logging
def on_connect(client, userdata, flags, rc):
    # If the connection was successful, subscribe to the frequency topic
    if rc == 0:
        logging.info("Verbunden mit dem Broker")
        client.subscribe(TOPIC_FREQUENCY)
        logging.info(f"Abonniere {TOPIC_FREQUENCY}")  
    else:
        logging.error(f"Verbindung fehlgeschlagen. Code: {rc}")


# Callback function for message logging
def on_publish(client, userdata, mid):
    logging.info(f"Nachricht mit ID {mid} veröffentlicht")


# Callback function for message handling
def on_message(client, userdata, message):
    logging.info(f"Nachricht empfangen: {message.payload.decode()}")

    # If it is a frequency message, update the send_message_interval
    if message.topic == TOPIC_FREQUENCY:
        # Set lock to ensure that the send frequency is not changed/read at the same time in the other thread
        with lock:
            global send_message_interval

            # Get frequency from payload and update the interval
            payload = json.loads(message.payload.decode())["payload"]
            send_message_interval = int(payload["frequency"])

            logging.info(f"Send interval changed to {send_message_interval} seconds")


# Set the callback functions
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

# Connect to the broker
client.connect(BROKER, PORT, keepalive=60)


def send_mqtt(data):
    """ Send humidity, temperature, and timestamp to the MQTT broker."""
    # If no data was provided, return without sending
    if data is None:
        return

    # Create humidity payload and send it to the MQTT broker
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

    # Create temperature payload and send it to the MQTT broker
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
    # start the MQTT client loop in a separate thread. Therefore messages with a new frequency can be received while sending data
    client.loop_start()

    # Read sensor data and send it to the MQTT broker
    while True:
        sensor_data = read_sensor()
        if sensor_data:  # ensure that sensor data is not None
            send_mqtt(sensor_data)

        # Set lock to ensure that the send frequency is not changed/read at the same time in the other thread
        with lock:
            time.sleep(send_message_interval)
