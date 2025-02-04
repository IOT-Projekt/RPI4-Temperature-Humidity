import time
import board
import adafruit_dht
import logging
import os

logging.basicConfig(level=logging.INFO)

def read_sensor():
    """ Reads temperature and humidity from the DHT22 sensor. Returns the values as a dictionary."""
    
    # Get the GPIO pin from the environment variable
    gpio_pin = os.getenv('DHT22_GPIO_PIN', 'D2')

    # Initialize the DHT22 sensor
    dhtDevice = adafruit_dht.DHT22(getattr(board, gpio_pin), use_pulseio=False)
    
    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return {
            "temperature_c": round(temperature_c, 1),
            "humidity": round(humidity, 1),
            "timestamp": time.time()
        }
    except RuntimeError as error:
        # if an error occurs, the error message should be logged
        logging.error(f"Fehler beim Lesen des Sensors: {error.args[0]}")
        return None
    except Exception as error:
        dhtDevice.exit()
        raise error