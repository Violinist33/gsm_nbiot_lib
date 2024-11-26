"""
Module for managing device connection and interaction with AT commands.

This module provides a `ConnectionManager` class that uses an AT command interface
to manage power control, APN configuration, and signal quality checking for a device.

Classes:
    - ConnectionManager: Manages the power and network configuration of a device.

Imports:
    - ATCommandInterface: Interface for sending and receiving AT commands.
    - ConnectionError: Exception for connection-related errors.
    - Pin: Microcontroller pin class for hardware interaction.

Example Usage:
    at_interface = ATCommandInterface(uart_port=0, baudrate=9600, timeout=5000)
    connection_manager = ConnectionManager(at_interface, "internet.apn")
    connection_manager.power_on(2)
    connection_manager.configure_apn()
    connection_manager.check_signal_quality()
"""

from .at_command import ATCommandInterface
from .errors import ConnectionError
from machine import Pin


class ConnectionManager:
    """
    Manages the connection and configuration of a device using AT commands.

    Attributes:
        at (ATCommandInterface): Interface for interacting with AT commands.
        apn (str): Access Point Name (APN) for network configuration.
        signal_quality (int): Signal quality value.
        lampIsOn (int): State of the lamp (1 for on, 0 for off).

    Methods:
        - power_on(pwr_en_pin): Powers on the device.
        - power_off(pwr_en_pin): Powers off the device.
        - configure_apn(): Configures the network APN for the device.
        - check_signal_quality(): Checks and updates the signal quality.
    """

    def __init__(self, at_interface: ATCommandInterface, apn: str):
        """
        Initializes the ConnectionManager.

        Args:
            at_interface (ATCommandInterface): AT command interface instance.
            apn (str): APN string for network configuration.
        """
        self.at = at_interface
        self.apn = apn
        self.signal_quality = 0
        self.lampIsOn = 1

    def power_on(self, pwr_en_pin):
        """
        Powers on the device by setting the power enable pin high.

        Args:
            pwr_en_pin (int): The GPIO pin number used for the power enable signal.
        """
        pwr_key = Pin(pwr_en_pin, Pin.OUT)
        pwr_key.value(1)

    def power_off(self, pwr_en_pin):
        """
        Powers off the device by setting the power enable pin low.

        Args:
            pwr_en_pin (int): The GPIO pin number used for the power enable signal.
        """
        pwr_key = Pin(pwr_en_pin, Pin.OUT)
        pwr_key.value(0)

    def configure_apn(self):
        """
        Configures the device's APN for network connectivity.

        Sends a series of AT commands to:
        - Disable functionality (AT+CFUN=0).
        - Set the default APN (AT*MCGDEFCONT).
        - Re-enable functionality (AT+CFUN=1).
        - Attach to the network (AT+CGATT?).
        - Retrieve connection parameters (AT+CGCONTRDP).
        """
        self.at.send_command("AT+CFUN=0")
        self.at.send_command(f'AT*MCGDEFCONT="IP","{self.apn}"')
        self.at.send_command("AT+CFUN=1")
        self.at.send_command("AT+CGATT?")
        self.at.send_command("AT+CGCONTRDP")

    def check_signal_quality(self):
        """
        Checks the device's signal quality.

        Sends the AT+CSQ command and updates the `signal_quality` attribute
        if the response contains valid signal quality data.

        Raises:
            ValueError: If the command response is invalid.
        """
        cmd, params = self.at.send_command("AT+CSQ")
        if cmd == "+CSQ" and params:
            self.signal_quality = int(params)
