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

with open('/data/options.json') as f:
    config = json.load(f)

client = mqtt.Client()
rfdevice = rpi_rf.RFDevice()
thSensor = th_sensor.THSensor()
timestamp = None
msgCount = -1
thLastData = {}

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

def deviceConfigObject(type, ha_id, id, ch, unit):
    configTHObject = {
        "device": configDeviceObject,
        "unit_of_measurement": unit,
        "state_topic": f"orchestrator/sensor/th_sensor/{ch}-{id}",
        "value_template": "{{ value_json." + type + " }}",
        "device_class": type,
        #"icon": "mdi:zigbee",
        "name": ha_id + '_' + type,
        "unique_id": ha_id + '_' + type,
        "object_id": ha_id + '_' + type,
        "origin": originObject,
    }
    return json.dumps(configTHObject)

def isOutsideChangeRate(data, lastData, tempChangeRate, humChangeRate):
    if lastData is None:
        return False

    tempChange = abs(data["temperature"] - lastData["temperature"])
    humChange = abs(data["humidity"] - lastData["humidity"])
    dt = data["timestamp"] - lastData["timestamp"]
    dt_mins = dt.total_seconds() / 60.0

    return tempChange > tempChangeRate * dt_mins or humChange > humChangeRate * dt_mins

client.username_pw_set(MQTT_USER, MQTT_PASS)
def on_message(client, userdata, msg):
    global timestamp
    global msgCount
    global thLastData
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
            
            dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            count = thSensor.isValid()
            if count >= 0 and count != msgCount:
                msgCount = count
                print(f"[{dt}] Header: {thSensor.getHeader()}, ID: {thSensor.getID()}, Battery: {thSensor.getBattery()}, TX Mode: {thSensor.getTXMode()}, Channel: {thSensor.getChannel()}, Temperature: {thSensor.getTemperature()}°C, Humidity: {thSensor.getHumidity()}%")
                data = {
                    "id": thSensor.getID(),
                    "battery": thSensor.getBattery(),
                    "tx_mode": thSensor.getTXMode(),
                    "channel": thSensor.getChannel(),
                    "temperature": thSensor.getTemperature(),
                    "humidity": thSensor.getHumidity(),
                    "timestamp": datetime.now(),
                }
                lastData = thLastData.get((data["id"], data["channel"]), None)

                if data["temperature"] < -20 or data["temperature"] > 60 or data["humidity"] < 10 or data["humidity"] > 95:
                    print(f"[{dt}] Data outside of the realistic: {data}")
                elif isOutsideChangeRate(data, lastData, 1.0, 1.0):
                    print(f"[{dt}] Data outside of the change rate: {data} - {lastData}")
                else:
                    client.publish(f"orchestrator/sensor/th_sensor/{thSensor.getChannel()}-{thSensor.getID()}", json.dumps(data, default=str), qos=1)
                    thLastData[(thSensor.getID(), thSensor.getChannel())] = data

                thSensorList = json.loads(config.get("th_sensor_list", "[]"))
                for thSensorCfg in thSensorList:
                    client.publish(f"homeassistant/sensor/{thSensorCfg['home_assistant_id']}_temperature/config",
                                   deviceConfigObject("temperature", thSensorCfg['home_assistant_id'], thSensorCfg['device_id'], thSensorCfg['channel'] - 1, "°C"), qos=1)
                    client.publish(f"homeassistant/sensor/{thSensorCfg['home_assistant_id']}_humidity/config", 
                                   deviceConfigObject("humidity", thSensorCfg['home_assistant_id'], thSensorCfg['device_id'], thSensorCfg['channel'] - 1, "%"), qos=1)
                    client.publish(f"homeassistant/sensor/{thSensorCfg['home_assistant_id']}_battery/config", 
                                   deviceConfigObject("battery", thSensorCfg['home_assistant_id'], thSensorCfg['device_id'], thSensorCfg['channel'] - 1, ""), qos=1)
            
            if rfdevice.rx_code_timestamp != timestamp:
                timestamp = rfdevice.rx_code_timestamp
                print(f"[{dt}] Code: {rfdevice.rx_code}, PulseLength: {rfdevice.rx_pulselength}, Protocol: {rfdevice.rx_proto}")

            #client.publish("homeassistant/sensor/th_sensor_0-60/config", json.dumps(configObject), qos=1)

    except Exception as e:
        print(f"MQTT error: {e}")


print(config)

client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)

print("📡 Listening for RF pulses to forward to Pilight...")
client.loop_forever()
