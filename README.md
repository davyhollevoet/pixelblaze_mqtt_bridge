# Pixelblaze-MQTT Bridge

Small service that connects a [pixelblaze](https://www.bhencke.com/pixelblaze) to MQTT.

Mainly written to work well with a [Home Assistant MQTT Light (default schema)](https://www.home-assistant.io/integrations/light.mqtt/#default-schema), but other MQTT-speaking things also work obviously.

It would be nicer to talk to the pixelblaze directly from [Home Assistant](https://www.home-assistant.io/), but this was way easier to make :)

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