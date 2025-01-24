# Instructions
I wanted to be able to control my air ventilation with Home Assistant.
This made it possible to implement useful functionality, such as 
- setting ventilation to away mode when nobody is at home
- boosting the ventilation when humidity around bathroom rises
- emergency off if smoke alarm is triggered

My device is Enervent Pingvin 120 and it has inputs for controlling the fan speed but not much else, so I needed to interface it with these pins with something smarter. 

## Hardware
I've had my old original Raspberry Pi unused in drawer for years. Now it was time to give it purpose again.
Controlling was not possible with only GPIO, so I needed also relays for this. Fortunately I had already built 3 relay card for my old project and also this was now recommissioned.

![RPi and relays](https://github.com/Jarauvi/enervent-pingvin-120-relay-control/blob/main/images/rpi_and_relays.jpg)

### Supplies needed
- Raspberry Pi (I had Pi1, but of course, this can be any model - just make sure the pinout is correct)
- Relays x 3
- 1k resistors x 3
- 1N4004 or equivalent diodes x 3
- (optional: or just 3x plug-and-play relay modules)
- (optional: connectors for easier installation, I used sugar cube connectors)

### Wiring
Enervent had pinout described in the ECC manual:

![Enervent pins](https://github.com/Jarauvi/enervent-pingvin-120-relay-control/blob/main/images/enervent_wiring.png)

I wired relays like shown in schematic:

![Wiring Raspberry and Pingvin](https://github.com/Jarauvi/enervent-pingvin-120-relay-control/blob/main/images/circuit.png)

### Connecting air ventilation unit
To expose board with external control connectors:
1. turn off the power and unplug air ventilation unit
2. open the big screws that close latch to rotary heat recovery unit
3. detach small maintenance latch on the right out of the way (screw was in the bottom of the door hinge if I remember it correcly)
4. open the small screws holding the panel that covers the board
5. wires can be fitted through the existing hole in the panel like shown in the image

![Opening air ventilation unit](https://github.com/Jarauvi/enervent-pingvin-120-relay-control/blob/main/images/opening_pingvin.png)

## Software
I made a simple MQTT client script to control the relays.
There are three topics for the fan speeds (away, normal and boost) and emergency shutdown of air ventilation.
MQTT client parameters can be configured from enervent.ini
