from datetime import datetime
import json
import rpi_rf
import time
import rpi_rf


class SwitchDataProcessor:

    def __init__(self, config, mqtt_client):
        self.rfdevice = rpi_rf.RFDevice()
        self.timestamp = None
        self.last_command = None
        self.config = config
        self.mqtt_client = mqtt_client

    def process_switch_command(self, msg):
        payload = msg.payload.decode()
        print(f"Received message on unexpected topic: {msg.topic} - {payload}")
        pack = json.loads(payload)

        selected_switch = next((s for s in self.config.get_rf_switch_list() if s["home_assistant_id"] == pack["id"]), None)
        if pack['state'] == "ON":
            print(f"Switch {pack['id']} {selected_switch['on_code']} is already ON, skipping transmission.")
            self.rfdevice.tx_code(selected_switch["on_code"], selected_switch["protocol"])
        else:
            print(f"Switch {pack['id']} {selected_switch['off_code']} is OFF, proceeding with transmission.")
            self.rfdevice.tx_code(selected_switch["off_code"], selected_switch["protocol"])

        pulse_list = " ".join(str(pulse) for pulse in self.rfdevice.pulses)
        pulse_list = f"1 {pulse_list} "
        # 7697411

        print(f"Transmitted RF code: {pulse_list}")
        self.mqtt_client.publish(f"rfproxys3/send/pulse_list", pulse_list, qos=1)
    
    def process_pulses(self, pulses):
        for timing in pulses:
            t = int(time.perf_counter() * 1000000)
            self.rfdevice.pushPulse(timing, t)
    
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.rfdevice.rx_code_timestamp != self.timestamp:
            self.timestamp = self.rfdevice.rx_code_timestamp
            self.last_command = {
                "code": self.rfdevice.rx_code,
                "protocol": self.rfdevice.rx_proto,
                "pulselength": self.rfdevice.rx_pulselength
            }
            self.mqtt_client.publish(f"orchestrator/switch/last", json.dumps(self.last_command), qos=1)
            print(f"[{ts}] Code: {self.rfdevice.rx_code}, PulseLength: {self.rfdevice.rx_pulselength}, Protocol: {self.rfdevice.rx_proto}")

            for switch in self.config.get_rf_switch_list():
                if switch["on_code"] == self.rfdevice.rx_code:
                    print(f"[{ts}] Switch {switch['home_assistant_id']} matched with ON code {self.rfdevice.rx_code}")
                    self.mqtt_client.publish(f"orchestrator/switch/{switch['home_assistant_id']}", "ON", qos=1)

                elif switch["off_code"] == self.rfdevice.rx_code:
                    print(f"[{ts}] Switch {switch['home_assistant_id']} matched with OFF code {self.rfdevice.rx_code}")
                    self.mqtt_client.publish(f"orchestrator/switch/{switch['home_assistant_id']}", "OFF", qos=1)
