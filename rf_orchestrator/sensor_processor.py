from datetime import datetime
import json
import th_sensor

class SensorDataProcessor:
    def __init__(self, config, mqtt_client):
        self.thSensor = th_sensor.THSensor()
        self.msgCount = -1
        self.thLastData = {}
        self.config = config
        self.mqtt_client = mqtt_client

    def is_valid_change(self, data, last_data, temp_rate=1.0, hum_rate=1.0):
        if last_data is None:
            return True
        temp_change = abs(data["temperature"] - last_data["temperature"])
        hum_change = abs(data["humidity"] - last_data["humidity"])
        dt = data["timestamp"] - last_data["timestamp"]
        return temp_change <= dt.total_seconds() * temp_rate and hum_change <= dt.total_seconds() * hum_rate

    def process_pulses(self, pulses):
        for timing in pulses:
            self.thSensor.pushPulse(timing)

            ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            count = self.thSensor.isValid()

            if count >= 0 and count != self.msgCount:
                self.msgCount = count
                data = {
                    "id": self.thSensor.getID(),
                    "battery": self.thSensor.getBattery(),
                    "tx_mode": self.thSensor.getTXMode(),
                    "channel": self.thSensor.getChannel(),
                    "temperature": self.thSensor.getTemperature(),
                    "humidity": self.thSensor.getHumidity(),
                    "timestamp": datetime.now(),
                }

                last_data = self.thLastData.get((data["id"], data["channel"]))

                if not (-20 <= data["temperature"] <= 60) or not (10 <= data["humidity"] <= 95):
                    print(f"[{ts}] Data outside of realistic range: {data}")
                elif not self.is_valid_change(data, last_data):
                    print(f"[{ts}] Data change rate too high: {data} - {last_data}")
                else:
                    self.thLastData[(data["id"], data["channel"])] = data
                    print(f"[{ts}] Header: {self.thSensor.getHeader()}, ID: {self.thSensor.getID()}, Battery: {self.thSensor.getBattery()}, TX Mode: {self.thSensor.getTXMode()}, Channel: {self.thSensor.getChannel()}, Temperature: {self.thSensor.getTemperature()}°C, Humidity: {self.thSensor.getHumidity()}%")
                    self.mqtt_client.publish(f"orchestrator/sensor/th_sensor/{self.thSensor.getChannel()}-{self.thSensor.getID()}", json.dumps(data, default=str), qos=1)
