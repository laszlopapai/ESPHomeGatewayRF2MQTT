import json
import time
import rpi_rf
import th_sensor
import paho.mqtt.client as mqtt
import numpy as np
from datetime import datetime

MQTT_BROKER = "192.168.1.31"
MQTT_PORT = 1883
MQTT_USER = "pilight"
MQTT_PASS = "asd123"
MQTT_TOPIC = "rfproxys3/sensor/pulse_list"

client = mqtt.Client()
rfdevice = rpi_rf.RFDevice()
thSensor = th_sensor.THSensor()
timestamp = None
msgCount = -1

configDeviceObject = {
    #"hw_version": "zStack12 20211115",
    "identifiers": [
        "rf_orchestrator_bridge"
    ],
    "manufacturer": "Laszlo Papai",
    "model": "RF Orchestrator bridge",
    "name": "RF Orchestrator",
    "sw_version": "1.0.0"
}

originObject = {
    "name": "RF Orchestrator",
    "sw": "1.0.0",
    "url": "https://github.com/laszlopapai/ESPHomeGatewayRF2MQTTo"
}

configObject = {
    "availability": [
        {
            "topic": "orchestrator/bridge/state",
            "value_template": "{{ value_json.state }}"
        }
    ],
    "availability_mode": "all",
    "device": configDeviceObject,
    "entity_category": "diagnostic",
    "icon": "mdi:zigbee",
    "name": "Version",
    "object_id": "rf_orchestrator_bridge_version",
    "origin": originObject,
    "state_topic": "orchestrator/bridge/info",
    "unique_id": "rf_orchestrator_bridge_version",
    "value_template": "{{ value_json.version }}"
}

def deviceConfigObject(name, type, id, ch, unit):
    configTHObject = {
        "device": configDeviceObject,
        "unit_of_measurement": unit,
        "state_topic": f"orchestrator/sensor/th_sensor/{ch}-{id}",
        "unique_id": f"rf_{type}_sensor_{ch}-{id}",
        "value_template": "{{ value_json." + type + " }}",
        "device_class": type,
        #"icon": "mdi:zigbee",
        "name": f"RF {name} {ch}CH {id}",
        "object_id": f"rf_{type}_sensor_{ch}-{id}",
        "origin": originObject,
    }
    return json.dumps(configTHObject)


client.username_pw_set(MQTT_USER, MQTT_PASS)
def on_message(client, userdata, msg):
    global timestamp
    global msgCount
    try:
        #data = base64.b64decode( msg.payload.decode() )
        #pulse_array = np.frombuffer(data, dtype=np.uint32)

        pulse_array = []
        data_str = msg.payload.decode().split(" ")
        for len_str in data_str:
            if len_str.isdigit():
                pulse_array = np.append(pulse_array, int(len_str))

        #print(len(pulse_array))

        #pulse_array = []
        for timing in pulse_array:
            t = int(time.perf_counter() * 1000000)
            rfdevice.pushPulse(timing, t)
            thSensor.pushPulse(timing)
            
            dt = datetime.now()
            count = thSensor.isValid()
            if count >= 0 and count != msgCount:
                msgCount = count
                print(f"[{dt.strftime("%Y-%m-%d %H:%M:%S")}] Header: {thSensor.getHeader()}, ID: {thSensor.getID()}, Battery: {thSensor.getBattery()}, TX Mode: {thSensor.getTXMode()}, Channel: {thSensor.getChannel()}, Temperature: {thSensor.getTemperature()}°C, Humidity: {thSensor.getHumidity()}%")
                data = {
                    "id": thSensor.getID(),
                    "battery": thSensor.getBattery(),
                    "tx_mode": thSensor.getTXMode(),
                    "channel": thSensor.getChannel(),
                    "temperature": thSensor.getTemperature(),
                    "humidity": thSensor.getHumidity()
                }
                client.publish(f"orchestrator/sensor/th_sensor/{thSensor.getChannel()}-{thSensor.getID()}", json.dumps(data), qos=1)

                client.publish("homeassistant/sensor/th_sensor_0-60_temperature/config", deviceConfigObject("Temperature", "temperature", 60, 0, "°C"), qos=1)
                client.publish("homeassistant/sensor/th_sensor_0-60_humidity/config", deviceConfigObject("Humidity", "humidity", 60, 0, "%"), qos=1)
                client.publish("homeassistant/sensor/th_sensor_0-60_battery/config", deviceConfigObject("Battery", "battery", 60, 0, ""), qos=1)

                client.publish("homeassistant/sensor/th_sensor_1-47_temperature/config", deviceConfigObject("Temperature", "temperature", 47, 1, "°C"), qos=1)
                client.publish("homeassistant/sensor/th_sensor_1-47_humidity/config", deviceConfigObject("Humidity", "humidity", 47, 1, "%"), qos=1)
                client.publish("homeassistant/sensor/th_sensor_1-47_battery/config", deviceConfigObject("Battery", "battery", 47, 1, ""), qos=1)

            
            if rfdevice.rx_code_timestamp != timestamp:
                timestamp = rfdevice.rx_code_timestamp
                print(f"[{dt.strftime("%Y-%m-%d %H:%M:%S")}] Code: {rfdevice.rx_code}, PulseLength: {rfdevice.rx_pulselength}, Protocol: {rfdevice.rx_proto}")

            #client.publish("homeassistant/sensor/th_sensor_0-60/config", json.dumps(configObject), qos=1)

    except Exception as e:
        print(f"MQTT error: {e}")

client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)

print("📡 Listening for RF pulses to forward to Pilight...")
client.loop_forever()
