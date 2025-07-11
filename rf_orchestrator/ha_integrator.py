
import json


class HAIntegrator:
    def __init__(self, config, mqtt_client):
        self.config = config
        self.mqtt_client = mqtt_client                
        self.configDeviceObject = {
            #"hw_version": "zStack12 20211115",
            "identifiers": [
                "rf_orchestrator_bridge"
            ],
            "manufacturer": "Laszlo Papai",
            "model": "RF Orchestrator bridge",
            "name": "RF Orchestrator",
            "sw_version": "1.0.0"
        }
        self.originObject = {
            "name": "RF Orchestrator",
            "sw": "1.0.0",
            "url": "https://github.com/laszlopapai/ESPHomeGatewayRF2MQTTo"
        }

    def promoteSensorEntity(self, id, unit, type, topic, jsonAttribute):
        configTHObject = {
            "device": self.configDeviceObject,
            "unit_of_measurement": unit,
            "state_topic": topic,
            "value_template": "{{ value_json." + jsonAttribute + " }}",
            "device_class": type,
            #"icon": "mdi:zigbee",
            "name": id,
            "unique_id": id,
            "object_id": id,
            "origin": self.originObject,
        }
        
        self.mqtt_client.publish(f"homeassistant/sensor/{id}/config", json.dumps(configTHObject), qos=1)
    
    def promoteSwitchEntity(self, id):
        configObject = {
            "device": self.configDeviceObject,

            "state_topic": f"orchestrator/switch/{id}",
            "command_topic": f"orchestrator/switch/command",

            "payload_on": "{ \"state\": \"ON\", \"id\": \"" + id + "\" }",
            "payload_off": "{ \"state\": \"OFF\", \"id\": \"" + id + "\" }",
            "state_on": "ON",
            "state_off": "OFF",
            "optimistic": True,
            
            #"icon": "mdi:zigbee",
            "name": id,
            "unique_id": id,
            "object_id": id,
            "origin": self.originObject,
        }
        
        self.mqtt_client.publish(f"homeassistant/switch/{id}/config", json.dumps(configObject), qos=1)


    def promoteConfigEntities(self):
        thSensorList = self.config.get_sensor_list()
        for thSensorCfg in thSensorList:
            topic = f"orchestrator/sensor/th_sensor/{thSensorCfg['channel'] - 1}-{thSensorCfg['device_id']}"
            self.promoteSensorEntity(
                thSensorCfg["home_assistant_id"] + "_temperature",
                "°C",
                "temperature",
                topic,
                "temperature"
            )
            self.promoteSensorEntity(
                thSensorCfg["home_assistant_id"] + "_humidity",
                "%",
                "humidity",
                topic,
                "humidity"
            )
            self.promoteSensorEntity(
                thSensorCfg["home_assistant_id"] + "_battery",
                "",
                "battery",
                topic,
                "battery"
            )

        rfSwitchList = self.config.get_rf_switch_list()
        for rfSwitchCfg in rfSwitchList:
            self.promoteSwitchEntity(
                rfSwitchCfg["home_assistant_id"]
            )
