import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port, user, password, message_callback):
        self.client = mqtt.Client()
        self.client.username_pw_set(user, password)
        self.client.on_message = message_callback
        self.client.connect(broker, port, 60)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    def publish(self, topic, payload, qos=1):
        self.client.publish(topic, payload, qos=qos)

    def loop_forever(self):
        self.client.loop_forever()