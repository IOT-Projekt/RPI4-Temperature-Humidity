import time
import board
import adafruit_dht

def read_sensor():
    """Liest Temperatur und Feuchtigkeit vom DHT22-Sensor."""
    dhtDevice = adafruit_dht.DHT22(board.D2, use_pulseio=False)
    
    try:
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        return {
            "temperature_c": round(temperature_c, 1),
            "humidity": round(humidity, 1),
            "timestamp": time.time()
        }
    except RuntimeError as error:
        # Fehler beim Lesen des Sensors
        print(f"Fehler beim Lesen des Sensors: {error.args[0]}")
        return None
    except Exception as error:
        dhtDevice.exit()
        raise error

if __name__ == "__main__":
    while True:
        data = read_sensor()
        if data:
            print(data)
        time.sleep(2.0)