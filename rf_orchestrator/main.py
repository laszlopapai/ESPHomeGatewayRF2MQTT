import config_loader
import mqtt_client
import ha_integrator
import sensor_processor
import switch_processor

def process_pulses(msg, sensor_list):
    try:
        pulse_array = []
        for val in msg.payload.decode().split(" "):
            if val.isdigit():
                pulse_array.append(int(val))
        for sensor in sensor_list:
            sensor.process_pulses(pulse_array)

    except Exception as e:
        print(f"MQTT error: {e}")


def main():

    def on_message(client, userdata, msg):
        if msg.topic == "rfproxys3/sensor/pulse_list":
            process_pulses(msg, [sensor, switch])
        elif msg.topic == "orchestrator/switch/command":
            switch.process_switch_command(msg)
        else:
            print(f"Unknown topic: {msg.topic}")

    config = config_loader.ConfigLoader()

    mqtt = mqtt_client.MQTTClient("192.168.1.31", 1883, "pilight", "asd123", on_message)
    mqtt.subscribe("rfproxys3/sensor/pulse_list")
    mqtt.subscribe("orchestrator/switch/command")

    haintegrator = ha_integrator.HAIntegrator(config, mqtt)
    sensor = sensor_processor.SensorDataProcessor(config, mqtt)
    switch = switch_processor.SwitchDataProcessor(config, mqtt)
    haintegrator.promoteConfigEntities()
    
    print("📡 Listening for RF pulses to forward to Pilight...")
    mqtt.loop_forever()


if __name__ == "__main__":
    main()
