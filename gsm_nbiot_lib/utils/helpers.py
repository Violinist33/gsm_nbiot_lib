"""
Module for utility helper functions in the GSM NB-IoT library.

This module provides various helper functions for data conversion, file operations,
power management, and LED control.

Functions:
    - hexStr_to_str(hex_str): Converts a hexadecimal string to a regular string.
    - str_to_hexStr(string): Converts a regular string to a hexadecimal string.
    - save_state(filename, variable, mode): Saves a variable's value to a file.
    - load_state(filename): Loads a variable's value from a file.
    - sleep_fn(time_min): Puts the device into deep sleep for a specified number of minutes.
    - led_blink(led_onboard, num_blinks, time_between): Blinks an onboard LED a specified number of times.

Imports:
    - binascii: For hexadecimal string manipulation.
    - utime: For time-related operations.
    - machine.Pin: For GPIO pin control.
    - machine.deepsleep: For putting the device into deep sleep.
"""

import binascii
import utime
from machine import Pin, deepsleep, lightsleep


def hexStr_to_str(hex_str):
    """
    Converts a hexadecimal string to a regular string.

    Args:
        hex_str (str): A string in hexadecimal format.

    Returns:
        str: The decoded regular string. Returns an empty string if conversion fails.

    Example:
        result = hexStr_to_str("48656c6c6f")  # result: "Hello"
    """
    try:
        return binascii.unhexlify(hex_str.encode('utf-8')).decode('utf-8')
    except binascii.Error:
        return ""


def str_to_hexStr(string):
    """
    Converts a regular string to a hexadecimal string.

    Args:
        string (str): A regular string.

    Returns:
        str: The encoded hexadecimal string.

    Example:
        result = str_to_hexStr("Hello")  # result: "48656c6c6f"
    """
    return binascii.hexlify(string.encode('utf-8')).decode('utf-8')


def save_state(filename, variable, mode='w'):
    """
    Saves a variable's value to a file.

    Args:
        filename (str): The name of the file.
        variable: The value to save (converted to string).
        mode (str): File open mode ('w' for overwrite, 'a' for append). Default is 'w'.

    Example:
        save_state("state.db", 42)
    """
    with open(filename, mode) as f:
        f.write(str(variable))


def load_state(filename):
    """
    Loads a variable's value from a file.

    If the file does not exist, it creates the file and initializes it with a default value of 0.

    Args:
        filename (str): The name of the file.

    Returns:
        str: The value read from the file.

    Example:
        value = load_state("state.db")  # value: "42" if the file contains 42
    """
    try:
        with open(filename, 'r') as f:
            return f.read()
    except OSError:
        save_state(filename, 0)  # Creates the file with a default value of 0
        return '0'


def sleep_fn(time_min):
    """
    Puts the device into deep sleep for a specified number of minutes.

    Args:
        time_min (float): Sleep duration in minutes.

    Example:
        sleep_fn(5)  # Puts the device into deep sleep for 5 minutes
    """
    print("Sleeping...")
    deepsleep(int(60000 * time_min))


def led_blink(led_onboard, num_blinks=4, time_between=0.5):
    """
    Blinks the onboard LED a specified number of times.

    Args:
        led_onboard (Pin): A Pin object representing the onboard LED.
        num_blinks (int): Number of blinks. Default is 4.
        time_between (float): Time in seconds between blinks. Default is 0.5.

    Example:
        led_blink(led_onboard, num_blinks=3, time_between=0.2)
    """
    print("Blinking LED...")

    prev = led_onboard.value()

    for _ in range(num_blinks):
        led_onboard.value(1)
        utime.sleep(time_between)
        led_onboard.value(0)
        utime.sleep(time_between)

    led_onboard.value(prev)
