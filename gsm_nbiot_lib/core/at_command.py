"""
Module for interacting with AT commands via UART.

This module provides functionality for sending AT commands to a device through UART
and handling the received responses.

Classes:
    - ATCommandInterface: Interface for sending AT commands and receiving responses.

Functions:
    Within the ATCommandInterface class:
        - __init__: Initializes the UART connection.
        - send_command: Sends an AT command and retrieves the response. Raises `ATCommandError` for errors or timeouts.
        - wait_response_line: Waits for a response line from UART. Handles timeout internally and returns "TIMEOUT" on failure.

    Outside the ATCommandInterface class:
        - sendCMD_waitRespLine: Sends a command, retries on failure, and processes the response.
        - send_command_with_retries: Sends a command with retries in case of errors or timeouts. Does not raise exceptions.

Imports:
    - utime: Used for time operations.
    - machine.UART: For initializing the UART connection.
    - gsm_nbiot_lib.core.command_parser.parse_response: For parsing responses.
    - gsm_nbiot_lib.core.errors.ATCommandError: Exception for AT command errors.
    - gsm_nbiot_lib.utils.helpers.sleep_fn: Helper function for delays.
"""

import utime
from machine import UART
from .command_parser import parse_response
from .errors import ATCommandError
from ..utils.helpers import sleep_fn
from ..models.command import info_cmd



class ATCommandInterface:
    """
    Interface for working with AT commands via UART.

    Attributes:
        uart (UART): UART object for data transmission.
        timeout (int): Timeout for waiting for a response in milliseconds.

    Methods:
        - __init__(uart_port, baudrate, timeout): Initializes the UART connection.
        - send_command(cmd, attempts, sleep_on_error): Sends a command and retrieves a response. Raises `ATCommandError` on failure.
        - wait_response_line(timeout): Waits for a response line. Returns "ERROR" or "TIMEOUT" for invalid responses or timeouts.
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
            ATCommandError: Raised if the response is "ERROR" or "TIMEOUT" even after retries.

        Notes:
            - Retries the command multiple times if the response is invalid or a timeout occurs.
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
        info_cmd(command_name, parameters)
        return command_name, parameters

    def wait_response_line(self):
        """
        Waits for a response from the device via UART.

        Args:
            timeout (int): Timeout in milliseconds for waiting for a response. Default is 5000.

        Returns:
            str: The response line, or special values "ERROR" or "TIMEOUT".

        Notes:
            - Reading stops if "OK", "ERROR", or "TIMEOUT" is found in the response.

        Exception Handling:
            - Handles timeouts internally by returning "TIMEOUT" if no valid response is received within the given time.
        """
        response = ""
        start_time = utime.ticks_ms()
        while (utime.ticks_ms() - start_time) < self.timeout:
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


# def sendCMD_waitRespLine(cmd, attempts=5, sleep_on_error=True, timeout=5000):
#     """
#     Sends an AT command, waits for the response, and processes it.
#
#     Args:
#         cmd (str): The AT command to send.
#         attempts (int): Number of retries in case of failure. Default is 5.
#         sleep_on_error (bool): Whether to introduce a delay before handling errors. Default is True.
#         timeout (int): Timeout in milliseconds for waiting for a response. Default is 5000.
#
#     Notes:
#         - This function uses `send_command_with_retries` for sending the command and handling retries.
#     """
#     response = send_command_with_retries(cmd, attempts, sleep_on_error, timeout)
#     command_name, parameters = parse_response(response)
#     print("Ім'я команди:", command_name)
#     print("Параметри:", parameters, "\n")
#     handle_command_response(command_name, parameters)
#
#
# def send_command_with_retries(cmd, attempts, sleep_on_error, timeout):
#     """
#     Sends a command and retries if a valid response is not received.
#
#     Args:
#         cmd (str): The AT command to send.
#         attempts (int): Number of retry attempts in case of failure.
#         sleep_on_error (bool): Whether to delay before handling errors.
#         timeout (int): Timeout in milliseconds for waiting for a response.
#
#     Returns:
#         str: The response from the device.
#
#     Notes:
#         - Does not raise exceptions; instead, it handles retries and returns the final response.
#     """
#     response = ""
#     for attempt in range(attempts):
#         print(f"Attempt {attempt}: {cmd}")
#         uart.write((cmd + '\r\n').encode())
#         response = waitRespLine(timeout)
#         if response and response not in ["ERROR", "TIMEOUT"]:
#             break
#         utime.sleep(1)
#
#     if sleep_on_error and response in ["ERROR", "TIMEOUT"]:
#         sleep_fn(0.1)
#
#     return response
