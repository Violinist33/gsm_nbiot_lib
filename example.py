# main.py
from sim7020py.commands import ATCommandError
from sim7020py.sim7020 import SIM7020
from sim7020py.blynk_integration import BlynkIntegration
from sim7020py.utils import save_state, load_state, parse_response
import utime
from machine import Pin, deepsleep, lightsleep

from config import *

# Initialize device and setup pins
led_onboard = Pin(LED_PIN, Pin.OUT)
led_main = Pin(LED_PIN_MAIN, Pin.OUT)
pwr_key = Pin(PWR_EN, Pin.OUT)

# Instantiate SIM7020 and Blynk classes
sim_7020 = SIM7020(port=UART_PORT, baudrate=UART_BAUDRATE)
blynk = BlynkIntegration(port=UART_PORT, apn=APN, blynk_token=BLYNK_TOKEN)

# Power control functions
def power_on():
    pwr_key.value(1)


def power_off():
    pwr_key.value(0)


# LED blink function
def led_blink(num_blinks=4, time_between=0.5):
    """Blinks the onboard LED a specified number of times."""
    prev = led_onboard.value()
    for _ in range(num_blinks):
        led_onboard.value(1)
        utime.sleep(time_between)
        led_onboard.value(0)
        utime.sleep(time_between)
    led_onboard.value(prev)


# Connect to network and initialize Blynk
def initialize_connection():
    power_on()
    sim_7020.initialize()
    sim_7020.set_apn(APN)
    sim_7020.connect_network()
    blynk.connect()


# Parse response (if needed as a standalone function)
def parse_at_response(response):
    command_name, parameters = parse_response(response)
    print("Command Name:", command_name)
    print("Parameters:", parameters)


# Example of sending AT commands and processing response
def send_and_process(cmd):
    try:
        response = sim_7020.at_command.send_command(cmd)
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
    led_main.value(lamp_is_on)
    led_onboard.value(not lamp_is_on)
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
        blynk.get_value("V0")

        # Toggle LED states based on lamp state
        lamp_is_on = not lamp_is_on
        save_state('state.db', lamp_is_on)
        led_main.value(lamp_is_on)
        led_onboard.value(not lamp_is_on)
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
