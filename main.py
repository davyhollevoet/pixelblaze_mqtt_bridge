import json
import time
import websocket
import paho.mqtt.client as mqtt
import logging
import sys
import yaml

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

with open("settings.yml", 'r') as stream:
    settings = yaml.safe_load(stream)


def on_message(ws, message):
    logging.info('Got WS message "%s"', message)


def on_error(ws, error):
    logging.error(error)


def on_close(ws):
    global current_ws
    current_ws = None


def on_open(ws):
    global current_ws

    logging.info("Websocket open")
    current_ws = ws

    if last_brightness is not None:
        set_brightness(last_brightness)


def set_brightness(b):
    global last_brightness

    last_brightness = b

    if current_ws is not None:
        current_ws.send(json.dumps({
            "brightness": b,
            "save": False
        }))


def set_active_program(p):
    if current_ws is not None:
        current_ws.send(json.dumps({
            "activeProgramId": p,
            "save": True
        }))


# The callback for when the client receives a CONNACK response from the server.
def on_mqtt_connect(client, userdata, flags, rc):
    logging.info('Connected to MQTT: %s', str(rc))
    client.subscribe(settings['mqtt_topic_prefix'] + '#')


def on_mqtt_message(client, userdata, msg):
    if msg.topic.startswith(settings['mqtt_topic_prefix']):
        logging.info('Received message "%s" for topic "%s" from MQTT', msg.payload, msg.topic)

        prop = msg.topic[len(settings['mqtt_topic_prefix']):]
        if prop == 'brightness':
            b = float(msg.payload)
            set_brightness(b)
        elif prop == 'active_program':
            set_active_program(msg.payload.decode("utf-8"))

        else:
            logging.warning('Got unhandled property message: "%s"', prop)
    else:
        logging.warning('Got unhandled topic message: "%s"', msg.topic)


current_ws = None
last_brightness = None

if __name__ == "__main__":
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message

    mqtt_client.username_pw_set(settings['mqtt_username'], settings['mqtt_password'])
    mqtt_client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pem')

    mqtt_client.connect(settings['mqtt_server'], 8883, 60)

    mqtt_client.loop_start()

    while True:
        # websocket.enableTrace(True)
        ws = websocket.WebSocketApp(
            settings['pixelblaze_address'],
            on_open=on_open,
            on_close=on_close,
            on_message=on_message,
            on_error=on_error
        )

        ws.run_forever(
            ping_interval=3,
            ping_timeout=2,
        )

        time.sleep(5)
