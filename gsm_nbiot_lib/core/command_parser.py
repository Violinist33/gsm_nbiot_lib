"""
Module for parsing and handling responses from AT commands.

This module provides functionality for parsing responses received from devices
via AT commands and processing them according to the command type.

Functions:
    - parse_response(response): Parses the raw response string into command name and parameters.
    - handle_command_response(command_name, parameters): Processes the response based on the command type.
    - handle_signal_quality(parameters): Processes the +CSQ (signal quality) command.

Imports:
    - None (depends on external usage context).

Example Usage:
    response = "+CSQ: 15,99"
    command_name, parameters = parse_response(response)
    handle_command_response(command_name, parameters)
"""


def parse_response(response):
    """
    Parses a raw AT command response string into the command name and parameters.

    Args:
        response (str): Raw response string from the AT command.

    Returns:
        tuple: A tuple containing the command name (str) and a list of parameters (list of str).
    """
    print("Response: ", response.strip("\r\n"))
    response = response.strip('\r\n')
    lines = response.split('\r\n')
    parts = lines[0].split(': ')
    command_name = parts[0].strip()
    parameters = []
    if len(parts) > 1:
        parameters = [param.strip().strip('"') for param in parts[1].split(',')]
    return command_name, parameters


def handle_command_response(command_name, parameters):
    """
    Processes the response based on the type of command.

    Args:
        command_name (str): The name of the command.
        parameters (list): A list of parameters associated with the command.
    """
    if command_name == "+CSQ":
        handle_signal_quality(parameters)
    elif command_name == "+CMQPUB":
        pass  # Reserved for future MQTT publish handling.


def handle_signal_quality(parameters):
    """
    Handles the +CSQ (signal quality) command.

    Args:
        parameters (list): Parameters of the +CSQ command.
    """
    global signal_quality
    signal_quality = parameters[0]
    print("Signal Quality:", signal_quality)

# def handle_mqtt_publish(parameters):
#     """
#     Handles the +CMQPUB (MQTT Publish) command.
#
#     Args:
#         parameters (list): Parameters of the +CMQPUB command.
#     """
#     lampIsOn = int(hexStr_to_str(parameters[-1].strip('"')))
#     lampIsOn = 1 if lampIsOn == 0 else 0
#     save_state('state.db', lampIsOn)
#     led_onboard.value(not lampIsOn)
#     led_main.value(lampIsOn)
#     print("Lamp state:", not lampIsOn)
