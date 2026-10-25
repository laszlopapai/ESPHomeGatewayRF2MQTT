import json
import platform

class ConfigLoader:
    def __init__(self):
        if platform.system() == "Windows":
            self.path = "data/options.json"
        else:
            self.path = "/data/options.json"

        with open(self.path) as f:
            self.config = json.load(f)
        print(self.config)

    def get_sensor_list(self):
        return json.loads(self.config.get("th_sensor_list", "[]"))

    def get_rf_switch_list(self):
        return json.loads(self.config.get("rf_switch_list", "[]"))

    def get_mqtt_host(self):
        return self.config.get("mqtt_host", "")

    def get_mqtt_port(self):
        return self.config.get("mqtt_port", "")

    def get_mqtt_user(self):
        return self.config.get("mqtt_user", "")

    def get_mqtt_pass(self):
        return self.config.get("mqtt_pass", "")
