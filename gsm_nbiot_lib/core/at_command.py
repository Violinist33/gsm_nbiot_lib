"""
Module for interacting with AT commands via UART.

This module provides functionality for sending AT commands to a device through UART
and handling the received responses.

Classes:
    - ATCommandInterface: Interface for sending AT commands and receiving responses.

Functions:
    Within the ATCommandInterface class:
        - __init__: Initializes the UART connection.
        - send_command: Sends an AT command and retrieves the response.
        - wait_response_line: Waits for a response line from UART.

Imports:
    - utime: Used for time operations.
    - machine.UART: For initializing the UART connection.
    - gsm_nbiot_lib.core.command_parser.parse_response: For parsing responses.
    - gsm_nbiot_lib.core.errors.ATCommandError: Exception for AT command errors.
    - gsm_nbiot_lib.utils.helpers.sleep_fn: Helper function for delays.
"""

import utime
from machine import UART
from gsm_nbiot_lib.core.command_parser import parse_response
from gsm_nbiot_lib.core.errors import ATCommandError
from gsm_nbiot_lib.utils.helpers import sleep_fn
from gsm_nbiot_lib.models.command import info_cmd


class ATCommandInterface:
    """
    Interface for working with AT commands via UART.

    Attributes:
        uart (UART): UART object for data transmission.
        timeout (int): Timeout for waiting for a response in milliseconds.

    Methods:
        - __init__(uart_port, baudrate, timeout): Initializes the UART connection.
        - send_command(cmd, attempts, sleep_on_error): Sends a command and retrieves a response.
        - wait_response_line(): Waits for a response line.
    """

    def __init__(self, uart_port=0, baudrate=115200, timeout=5000):
        """
        Initializes the UART connection.

        Args:
            uart_port (int): UART port number. Default is 0.
            baudrate (int): Data transfer rate. Default is 115200.
            timeout (int): Timeout for waiting for a response in milliseconds. Default is 5000.
        """
        self.uart = UART(uart_port, baudrate=baudrate, bits=8, parity=None, stop=1)
        self.timeout = timeout

    def send_command(self, cmd, attempts=5, sleep_on_error=True):
        """
        Sends an AT command and waits for a response.

        Args:
            cmd (str): The AT command to send.
            attempts (int): Number of retry attempts in case of failure. Default is 5.
            sleep_on_error (bool): Delay before raising an exception. Default is True.

        Returns:
            tuple: Command name and its parameters.

        Raises:
            ATCommandError: If the response contains "ERROR" or "TIMEOUT".
        """
        response = ""
        for attempt in range(attempts):
            print(f"Attempt {attempt + 1}: {cmd}")
            self.uart.write((cmd + '\r\n').encode())
            response = self.wait_response_line()
            if response and response not in ["ERROR", "TIMEOUT"]:
                break
            utime.sleep(1)

        if sleep_on_error and response in ["ERROR", "TIMEOUT"]:
            sleep_fn(0.1)
            raise ATCommandError(f"Command '{cmd}' failed with response: {response}")

        command_name, parameters = parse_response(response)
        if parameters:
            info_cmd(command_name, parameters)
        return command_name, parameters

    def wait_response_line(self, timeout=5000):
        """
        Waits for a response from the device via UART.

        Args:
            timeout (int): Timeout in milliseconds for waiting for a response. Default is 5000.

        Returns:
            str: The response line, or special values "ERROR" or "TIMEOUT".

        Notes:
            - Reading stops if "OK", "ERROR", or "TIMEOUT" is found in the response.
        """
        response = ""
        start_time = utime.ticks_ms()
        while (utime.ticks_ms() - start_time) < timeout:
            if self.uart.any():
                char = self.uart.read(1).decode()
                response += char
                if response.endswith("OK\r\n") or response.endswith("ERROR\r\n") or response.endswith("TIMEOUT\r\n"):
                    break
        if response.endswith("OK\r\n"):
            return response
        elif response.endswith("ERROR\r\n"):
            return "ERROR"
        elif response.endswith("TIMEOUT\r\n") or not response:
            return "TIMEOUT"
        return response
