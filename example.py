# main.py
from sim7020py.commands import ATCommandError
from sim7020py.sim7020 import SIM7020
from sim7020py.blynk_integration import BlynkIntegration
from sim7020py.utils import save_state, load_state, parse_response
import utime
from machine import Pin, deepsleep, lightsleep

from config import *


# Power control functions
def power_on():
    PWR_KEY.value(1)


def power_off():
    PWR_KEY.value(0)


# LED blink function
def led_blink(num_blinks=4, time_between=0.5):
    """Blinks the onboard LED a specified number of times."""
    prev = LED_ONBOARD.value()
    for _ in range(num_blinks):
        LED_ONBOARD.value(1)
        utime.sleep(time_between)
        LED_ONBOARD.value(0)
        utime.sleep(time_between)
    LED_ONBOARD.value(prev)


# Connect to network and initialize Blynk
def initialize_connection():
    power_on()
    SIM_7020.initialize()
    SIM_7020.set_apn(APN)
    SIM_7020.connect_network()
    BLYNK.connect()


# Parse response (if needed as a standalone function)
def parse_at_response(response):
    command_name, parameters = parse_response(response)
    print("Command Name:", command_name)
    print("Parameters:", parameters)


# Example of sending AT commands and processing response
def send_and_process(cmd):
    try:
        response = SIM_7020.at_command.send_command(cmd)
        parse_at_response(response)
    except ATCommandError as e:
        print(f"Error: {e}")


# MQTT connection setup
def mqtt_connect():
    send_and_process("AT+CSQ")  # Check signal strength
    send_and_process(f"AT+CMQNEW=\"{BROKER_ADDRESS}\",\"1883\",12000,1024")
    send_and_process(f"AT+CMQCON=0,3,\"{DEVICE_NAME}\",45,1,0,\"device\",\"{DEVICE_SECRET}\"")


# State management
def toggle_lamp_state(state_file='state.db'):
    current_state = load_state(state_file)
    lamp_is_on = int(current_state) if current_state else 1
    LED_MAIN.value(lamp_is_on)
    LED_ONBOARD.value(not lamp_is_on)
    return lamp_is_on


def main():
    # Initialize connection and setup Blynk
    initialize_connection()
    lamp_is_on = toggle_lamp_state()

    # Blink LED on startup
    led_blink(5)

    # Main loop
    while True:
        print("Checking for commands...")
        # Request the value of a pin from Blynk
        BLYNK.get_value("V0")

        # Toggle LED states based on lamp state
        lamp_is_on = not lamp_is_on
        save_state('state.db', lamp_is_on)
        LED_MAIN.value(lamp_is_on)
        LED_ONBOARD.value(not lamp_is_on)
        utime.sleep(2)  # Add a delay

        # Example of sending and receiving data over MQTT (if needed)
        mqtt_connect()

        # Sleep or perform low-power tasks
        print("Entering light sleep mode...")
        led_blink(4, 0.5)
        lightsleep(10000)
        led_blink(10, 0.05)

    # Power down when finished
    power_off()
    print("Device going to deep sleep...")
    deepsleep(15 * 60000)


if __name__ == "__main__":
    main()
