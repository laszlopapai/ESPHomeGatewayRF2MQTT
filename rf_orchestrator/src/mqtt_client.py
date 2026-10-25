import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port, user, password, message_callback, connect_callback=None):
        self.topics = []
        self.connect_callback = connect_callback
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(user, password)
        self.client.on_connect = self._on_connect
        self.client.on_message = message_callback
        self.client.connect(broker, port, 60)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code.is_failure:
            print(f"MQTT connection failed: {reason_code}")
            return

        print("MQTT connected")
        # Subscriptions are lost when the broker connection drops, renew them on every (re)connect
        for topic in self.topics:
            self.client.subscribe(topic)

        if self.connect_callback:
            self.connect_callback()

    def subscribe(self, topic):
        self.topics.append(topic)
        if self.client.is_connected():
            self.client.subscribe(topic)

    def publish(self, topic, payload, qos=1, retain=False):
        self.client.publish(topic, payload, qos=qos, retain=retain)

    def loop_forever(self):
        self.client.loop_forever()
