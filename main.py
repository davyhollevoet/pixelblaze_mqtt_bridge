import json
import sys

import logging
import paho.mqtt.client as mqtt
import time
import websocket
import yaml

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

with open("settings.yml", 'r') as stream:
    settings = yaml.safe_load(stream)

programs = {}


def parse_programs_frame(b):
    s = b.decode("utf8")
    for l in s.split('\n'):
        p = l.split('\t')
        if len(p[0]) > 0:
            programs[p[1]] = p[0]


def save_programs():
    with open("programs.yml", "w+") as p:
        yaml.dump({v: k for k, v in programs.items()}, p)


def on_message(ws, message):
    if message[0] is 0x07:
        if message[1] & 0x01 == 0x01:
            programs.clear()
        parse_programs_frame(message[2:])
        if message[1] & 0x04 == 0x04:
            save_programs()
    else:
        logging.info('Got WS message "%s"', message)


def on_error(ws, error):
    logging.error(error)


def on_close(ws):
    global current_ws
    current_ws = None


def ws_send(p):
    if current_ws is not None:
        logging.debug("Sending %s", json.dumps(p))
        current_ws.send(json.dumps(p))


def on_open(ws):
    global current_ws

    logging.info("Websocket open")
    current_ws = ws

    ws_send({
        "listPrograms": True
    })

    if last_brightness is not None:
        set_brightness(last_brightness)


def set_brightness(b):
    global last_brightness

    last_brightness = b

    ws_send({
        "brightness": b,
        "save": False
    })


def set_switch(s):
    global last_brightness

    ws_send({
        "brightness": last_brightness if s else 0,
        "save": False
    })


def set_active_program(p):
    global last_program

    last_program = programs.get(p, p)
    ws_send({
        "activeProgramId": last_program,
        "save": False
    })


def set_hs(p):
    global last_program
    if last_program != settings["ext_color_prog"]:
        set_active_program(settings["ext_color_prog"])

    try:
        h, s = map(lambda x: float(x), p.split(','))
        ws_send({
            "setVars": {
                "ext_h": h / 360.0,
                "ext_s": s / 100.0
            }
        })
    except ValueError:
        logging.error("Could not parse payload")


# The callback for when the client receives a CONNACK response from the server.
def on_mqtt_connect(client, userdata, flags, rc):
    logging.info('Connected to MQTT: %s', str(rc))
    client.subscribe(settings['mqtt_topic_prefix'] + '#')


def on_mqtt_message(client, userdata, msg):
    if msg.topic.startswith(settings['mqtt_topic_prefix']):
        logging.info('Received message "%s" for topic "%s" from MQTT', msg.payload, msg.topic)

        prop = msg.topic[len(settings['mqtt_topic_prefix']):]
        if prop == 'brightness':
            b = float(msg.payload) / 255.0
            set_brightness(b)
        elif prop == 'switch':
            set_switch(msg.payload.decode("utf8") == "ON")
        elif prop == 'active_program':
            set_active_program(msg.payload.decode("utf-8"))
        elif prop == 'hs':
            set_hs(msg.payload.decode("utf-8"))

        else:
            logging.warning('Got unhandled property message: "%s"', prop)
    else:
        logging.warning('Got unhandled topic message: "%s"', msg.topic)


current_ws = None
last_brightness = None
last_program = None

if __name__ == "__main__":
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message

    mqtt_client.username_pw_set(settings['mqtt_username'], settings['mqtt_password'])
    mqtt_client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pem')

    mqtt_client.connect(settings['mqtt_server'], settings.get('mqtt_port', 8883), 60)

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
