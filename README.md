# Pixelblaze-MQTT Bridge

Small service that connects a [pixelblaze](https://www.bhencke.com/pixelblaze) to MQTT.

Mainly written to work well with a [Home Assistant MQTT Light (default schema)](https://www.home-assistant.io/integrations/light.mqtt/#default-schema), but other MQTT-speaking things also work obviously.

It would be nicer to talk to the pixelblaze directly from [Home Assistant](https://www.home-assistant.io/), but this was way easier to make :)

## Settings
```yaml
---
mqtt_server: ...
mqtt_username: ...
mqtt_password: ...
# The bridge will subscribe to $mqtt_topic_prefix + '#' and publish to $mqtt_topic_prefix + 'available'
mqtt_topic_prefix: lights/pixelblaze/
# Websocket url of the pixelblaze instance. Yes, only a single instance is supported for now
pixelblaze_address: ws://...:81/
# Name or id of a pattern that supports two parameters: ext_h and ext_s. The bridge switches to this
# pattern when something is published to $mqtt_topic_prefix + 'hs'
ext_color_prog: .................
```

## ext_color_prog
When you select a single color for your light in Home Assistant (set up with the configuration below), it publishes H and S to `hs_command_topic`. The bridge will first switch the pixelblaze to the `ext_color_prog` pattern (if needed) and then sets H and S.

What `ext_color_prog` shows, is up to you: only that color, that color with something else modulated on top,...

The example below shows a single color with a [mexican hat-shaped](https://subsurfwiki.org/wiki/Ricker_wavelet) color displacement on top of it. The hat slowly moves between the endpoints of the leds. The base color can be controlled with a color picker in the pixelblaze web interface, or over a Websocket connection, like the bridge does: it updates `ext_h` and `ext_s` when something is published to `hs_command_topic`.
```js
export var ext_h = 0.22
export var ext_s = 1
export var ext_v = 1

// You might want to tweak these values to suit your leds
var sigma = 0.07
var f = 2/(sqrt(3*sigma)*pow(PI, 0.25))

export function beforeRender(delta) {
  t1 = time(10)
  t2 = triangle(t1)
  ss = sigma * sigma
}

export function render(index) {
  t = (index/pixelCount) - t2
  tt = t*t
  h = ext_h + f*(1-tt/ss)*exp(-tt/(2*ss))/10.0
  hsv(h, ext_s, ext_v)
}

export function hsvPickerColor(h, s, v)
{
  ext_h = h
  ext_s = s
  ext_v = v
}
```

## Home Assistant
Example configuration for a [Home Assistant MQTT Light](https://www.home-assistant.io/integrations/light.mqtt/)

```yaml
light:
  - platform: mqtt
    command_topic: "lights/pixelblaze/switch"
    brightness_command_topic: "lights/pixelblaze/brightness"
    hs_command_topic: "lights/pixelblaze/hs"
    effect_command_topic: "lights/pixelblaze/active_program"
    availability_topic: "lights/pixelblaze/available"
    effect_list:
      - opposites
      - spin cycle
      - rainbow fonts
      - modes and waveforms
      - green ripple reflections
      - marching rainbow
      - color twinkles
      - firework dust
      - block reflections
      - color bands
      - color hues
      - glitch bands
      - sparks
      - rainbow melt
```