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
