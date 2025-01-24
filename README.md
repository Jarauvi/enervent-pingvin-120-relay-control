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

### Supplies needed
- Raspberry Pi (I had Pi1, but of course, this can be any model - just make sure the pinout is correct)
- Relays x 3
- 1k resistors x 3
- 1N4004 or equivalent diodes x 3
- (optional: or just 3x plug-and-play relay modules)
- (optional: connectors for easier installation, I used sugar cube connectors)

### Wiring
I wired relays like shown in schematic:


Air ventilation unit 

## Software
I made a simple MQTT client script to control the relays.
There are three topics for the fan speeds (away, normal and boost) and emergency shutdown of air ventilation.
MQTT client parameters can be configured from enervent.ini
