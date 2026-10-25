import config_loader
import mqtt_client
import ha_integrator
from processors import sensor_processor
from processors import switch_processor

# The gateway sends one frame per message without the idle gap that ended it, but the decoders
# detect frame boundaries from long gaps, so one is appended after every frame
FRAME_END_GAP = 100000

def process_pulses(msg, sensor_list):
    try:
        pulse_array = []
        for val in msg.payload.decode().split():
            if val.lstrip("-").isdigit():
                # Signed durations: positive = high, negative = low; the decoders only use lengths
                pulse_array.append(abs(int(val)))
        pulse_array.append(FRAME_END_GAP)
        for sensor in sensor_list:
            sensor.process_pulses(pulse_array)

    except Exception as e:
        print(f"MQTT error: {e}")


def main():

    def on_message(client, userdata, msg):
        if msg.topic == gateway_rx_topic:
            process_pulses(msg, [sensor, switch])
        elif msg.topic == "orchestrator/switch/command":
            switch.process_switch_command(msg)
        elif msg.topic == "homeassistant/status":
            # HA announces "online" after a restart, discovery has to be sent again
            if msg.payload.decode() == "online":
                haintegrator.promoteConfigEntities()
        else:
            print(f"Unknown topic: {msg.topic}")

    def on_connect():
        haintegrator.promoteConfigEntities()

    config = config_loader.ConfigLoader()
    gateway_rx_topic = f"{config.get_gateway_topic_prefix()}/rx"

    mqtt = mqtt_client.MQTTClient(config.get_mqtt_host(), config.get_mqtt_port(), config.get_mqtt_user(), config.get_mqtt_pass(), on_message, on_connect)
    mqtt.subscribe(gateway_rx_topic)
    mqtt.subscribe("orchestrator/switch/command")
    mqtt.subscribe("homeassistant/status")

    haintegrator = ha_integrator.HAIntegrator(config, mqtt)
    sensor = sensor_processor.SensorDataProcessor(config, mqtt)
    switch = switch_processor.SwitchDataProcessor(config, mqtt)

    print("📡 Listening for RF pulses to forward to Pilight...")
    mqtt.loop_forever()


if __name__ == "__main__":
    main()
