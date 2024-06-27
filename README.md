# ESPHome for Nixie2

Includes custom component for HV5222 low-side shift register

Read more [here](https://vigue.me/s/vixen)

Example configuration:

```yaml
esphome:
  name: nixieclock
  friendly_name: nixieclock
  on_boot:
    then:
      - number.set:
          id: nixie_1
          value: 9
      - number.set:
          id: nixie_2
          value: 9
      - number.set:
          id: nixie_3
          value: 9
      - number.set:
          id: nixie_4
          value: 9
      - number.set:
          id: nixie_5
          value: 9
      - number.set:
          id: nixie_6
          value: 9

esp32:
  board: esp32-s3-devkitc-1
  framework:
    type: esp-idf

# Enable logging
logger:
  level: WARN

external_components:
  - source: github://acvigue/esphome-nixie2
    components: [hv5222]
    refresh: 1s

# Enable Home Assistant API
api:
  encryption:
    key: "##########"

ota:
  - platform: esphome
    password: "##########"

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

  # Enable fallback hotspot (captive portal) in case wifi connection fails
  ap:
    ssid: "Nixieclock Fallback Hotspot"
    password: "##########"

globals:
  - id: military_time
    type: bool
    restore_value: yes
    initial_value: "false"
  - id: cleaning
    type: bool
    restore_value: no
    initial_value: "false"

light:
  - platform: esp32_rmt_led_strip
    rgb_order: GRB
    pin: 21
    num_leds: 6
    rmt_channel: 1
    chipset: ws2812
    is_rgbw: True
    name: "Backlight"
    restore_mode: RESTORE_DEFAULT_OFF
  - platform: monochromatic
    output: calibrated_oe_out
    id: oe
    name: "HV5222 OE"
    restore_mode: RESTORE_DEFAULT_OFF

spi:
  id: spi_hv5222
  clk_pin: 12
  mosi_pin: 10
  interface: software

hv5222:
  - id: myHV5222
    spi_id: spi_hv5222
    data_rate: 10MHz
    spi_mode: MODE0
    count: 2

output:
  - platform: ledc
    pin: 11
    frequency: 18kHz
    id: oe_out
    inverted: True
  - platform: template
    id: calibrated_oe_out
    type: float
    write_action:
      - if:
          condition:
            lambda: return state > 0;
          then:
            - output.set_level:
                id: oe_out
                level: !lambda |-
                  const int min_percentage=40;
                  float min=static_cast<float>(min_percentage)/100.0f;
                  float k=(1.0f-min)/0.99f;
                  float m=(0.99f-1.0f+min)/0.99f;
                  return k*state+m;
          else:
            - output.set_level:
                id: oe_out
                level: 0

number:
  - platform: hv5222
    id: nixie_6
    count_back: True
    count_back_speed: 50
    hv5222: myHV5222
    pins: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  - platform: hv5222
    id: nixie_5
    count_back: True
    count_back_speed: 50
    hv5222: myHV5222
    pins: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
  - platform: hv5222
    id: nixie_4
    count_back: True
    count_back_speed: 50
    hv5222: myHV5222
    pins: [20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
  - platform: hv5222
    id: nixie_3
    count_back: True
    count_back_speed: 50
    hv5222: myHV5222
    pins: [30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
  - platform: hv5222
    id: nixie_2
    count_back: True
    count_back_speed: 50
    hv5222: myHV5222
    pins: [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
  - platform: hv5222
    id: nixie_1
    count_back: True
    count_back_speed: 50
    hv5222: myHV5222
    pins: [50, 51, 52, 53, 54, 55, 56, 57, 58, 59]

time:
  - platform: sntp
    id: sntp_time
    on_time:
      - cron: "0 0 * * * *"
        then:
          - globals.set:
              id: cleaning
              value: "true"
          - repeat:
              count: 45
              then:
                - number.increment:
                    id: nixie_1
                - number.increment:
                    id: nixie_2
                - number.increment:
                    id: nixie_3
                - number.increment:
                    id: nixie_4
                - number.increment:
                    id: nixie_5
                - number.increment:
                    id: nixie_6
                - delay: 0.25s
          - globals.set:
              id: cleaning
              value: "false"
      - cron: "* * * * * *"
        then:
          lambda: |
            if(!id(cleaning)) {
            auto time = id(sntp_time).now();
            auto call1 = id(nixie_1).make_call();
            call1.set_value(time.second % 10);
            call1.perform();
            auto call2 = id(nixie_2).make_call();
            call2.set_value(time.second / 10);
            call2.perform();
            auto call3 = id(nixie_3).make_call();
            call3.set_value(time.minute % 10);
            call3.perform();
            auto call4 = id(nixie_4).make_call();
            call4.set_value(time.minute / 10);
            call4.perform();
            auto hours = time.hour;
            if(!id(military_time)) {
            hours = hours % 12;
            if (hours == 0) hours = 12;
            }
            auto call5 = id(nixie_5).make_call();
            call5.set_value(hours % 10);
            call5.perform();
            auto call6 = id(nixie_6).make_call();
            call6.set_value(hours / 10);
            call6.perform();
            }

captive_portal:
```
