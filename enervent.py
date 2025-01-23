#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from time import sleep
import logging
import RPi.GPIO as GPIO
import configparser
import os.path

# read config
cp = configparser.ConfigParser()
try:
  if os.path.exists('/boot/enervent.ini'):
    cp.read('/boot/enervent.ini')
  elif os.path.exists('enervent.ini'):
    cp.read('enervent.ini')
except Exception as ex:
  print(f'Error: {ex}')
  exit()

# set up logging
logger = logging.getLogger('enervent')

#read GPIO pins for relays
AWAY_PIN = cp['MQTT'].getint('away_pin') #27 by default
logger.debug(f"AWAY_PIN: {AWAY_PIN}")
NORMAL_PIN = cp['MQTT'].getint('normal_pin') #22 by default
logger.debug(f"NORMAL_PIN: {NORMAL_PIN}")
BOOST_PIN = cp['MQTT'].getint('boost_pin') #23 by default
logger.debug(f"BOOST_PIN: {BOOST_PIN}")

# Read settings for MQTT broker
broker_ip = cp['MQTT'].get('broker_ip')
logger.debug(f"Broker ip: {broker_ip}")
broker_port = cp['MQTT'].getint('broker_port')
logger.debug(f"Broker port: {broker_port}")
broker_timeout = cp['MQTT'].getint('broker_timeout')
logger.debug(f"Broker timeout: {broker_timeout}")
publish_retain = cp['MQTT'].getboolean('publish_retain')
logger.debug(f"Publish retain: {publish_retain}")
topic_sub = cp['MQTT'].get('topic_sub')
logger.debug(f"Topic sub: {topic_sub}")
topic_away = cp['MQTT'].get('topic_out1')
logger.debug(f"Topic away mode: {topic_away}")
topic_normal = cp['MQTT'].get('topic_out2')
logger.debug(f"Topic normal mode: {topic_normal}")
topic_boost = cp['MQTT'].get('topic_out3')
logger.debug(f"Topic boost mode: {topic_boost}")
topic_emergency_off = cp['MQTT'].get('topic_emergency_off')
logger.debug(f"Topic emergency off: {topic_emergency_off}")
username = cp['MQTT'].get('username')
password = cp['MQTT'].get('password')

# set pins and default pin states. By default, NORMAL_MODE is always on at startup
# these are needed for tracking the input states
AWAY_MODE = {'pin': AWAY_PIN, 'topic': topic_away, 'state': 'OFF'}
NORMAL_MODE = {'pin': NORMAL_PIN, 'topic': topic_normal, 'state': 'ON'}
BOOST_MODE = {'pin': BOOST_PIN, 'topic': topic_boost, 'state': 'OFF'}

# Setup array of relay states
relay_states = [AWAY_MODE, NORMAL_MODE, BOOST_MODE]

# set GPIO mode and pin states
GPIO.setmode(GPIO.BCM)
GPIO.setup(AWAY_PIN, GPIO.OUT)
GPIO.output(AWAY_PIN, GPIO.LOW)
GPIO.setup(NORMAL_PIN, GPIO.OUT)
GPIO.output(NORMAL_PIN, GPIO.HIGH)
GPIO.setup(BOOST_MODE, GPIO.OUT)
GPIO.output(BOOST_MODE, GPIO.LOW)

def main():
  def on_connect(client, userdata, flags, rc, misc):
    """MQTT server is connected."""

    logger.info("Connected with result code "+str(rc))
    client.subscribe(topic_sub)
   
  def on_message(client, userdata, msg):
    """ When control message is received, 
        toggle relay states and sleep for a while
    """
    if msg.topic == topic_away:
      if msg.payload == b"ON" :
        logger.info("Away command received")
        update_relay_state(0)
        sleep(.1)
    if msg.topic == topic_normal:
      if msg.payload == b"ON" :
        logger.info("Normal command received")
        update_relay_state(1)
        sleep(.1)
    if msg.topic == topic_boost:
      if msg.payload == b"ON" :
        logger.info("Boost command received")
        update_relay_state(2)
        sleep(.1)
    if msg.topic == topic_emergency_off:
      if msg.payload == b"ON" :
        logger.info("EMERGENCY OFF COMMAND RECEIVED")
        # set all pins LOW
        GPIO.output(relay_states[0]['pin'], GPIO.LOW)
        logger.debug(f"{AWAY_PIN}: LOW")
        client.publish(topic_away, 'OFF', retain=publish_retain)
        logger.debug(f"{topic_away}: OFF")
        GPIO.output(relay_states[1]['pin'], GPIO.LOW)
        logger.debug(f"{NORMAL_PIN}: LOW")
        client.publish(topic_normal, 'OFF', retain=publish_retain)
        logger.debug(f"{topic_normal}: OFF")
        GPIO.output(relay_states[2]['pin'], GPIO.LOW)
        logger.debug(f"{BOOST_PIN}: LOW")
        client.publish(topic_boost, 'OFF', retain=publish_retain)
        logger.debug(f"{topic_boost}: OFF")

  def update_relay_state(index):
      """Update relay state and control relays."""

      # if all relays are LOW, update emergency off state
      if relay_states[0]['state'] == 'OFF' and relay_states[1]['state'] == 'OFF' and relay_states[2]['state'] == 'OFF':
        client.publish(topic_emergency_off, 'OFF', retain=publish_retain)
        logger.debug(f"{topic_emergency_off}: OFF")
    
      # Toggle current relay
      if relay_states[index]['state'] != 'ON':
          GPIO.output(relay_states[index]['pin'], GPIO.HIGH)
          logger.debug(f"{relay_states[index]['pin']}: HIGH")
          # update relay_states array item
          relay_states[index]['state'] = 'ON'

      # wait before toggling LOW other relays
      sleep(3.0)

      # Turn LOW other relays
      for i, relay in enumerate(relay_states):
          if i != index and relay['state'] != 'OFF':
              GPIO.output(relay['pin'], GPIO.LOW)
              logger.debug(f"{relay['pin']}: LOW")
              client.publish(relay['topic'], 'OFF', retain=publish_retain)
              logger.debug(f'{relay['topic']}: OFF')
              relay['state'] = "OFF"
  
  # initialize logger
  log_level = cp['LOGGING'].get('log_level')
  logging.basicConfig(level=log_level)

  # set up mqtt client and callbacks
  client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
  client.on_connect = on_connect
  client.on_message = on_message

  # attempt to connect
  client.connect(broker_ip, broker_port, broker_timeout)
  client.username_pw_set(username=username, password=password)

  client.publish(topic_away, 'OFF', retain=publish_retain)
  client.publish(topic_normal, 'ON', retain=publish_retain)
  client.publish(topic_boost, 'OFF', retain=publish_retain)
  client.publish(topic_emergency_off, 'OFF', retain=publish_retain)

  client.loop_forever()

if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    logger.info('Keyboard interrupt: exiting...')