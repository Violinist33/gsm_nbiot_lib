"""
Module for SIM7020 NB-IoT device management.

This module provides the `SIM7020` class for managing a SIM7020 device,
extending the `ConnectionManager` to include specific functionality
like loading, saving, and toggling the state of a lamp.

Classes:
    - SIM7020: A specialized connection manager for SIM7020 devices.

Imports:
    - ConnectionManager: Base class for managing device connections.
    - ATCommandInterface: Interface for sending and receiving AT commands.
    - save_state: Utility function to save state to a database.
    - load_state: Utility function to load state from a database.

Example Usage:
    sim = SIM7020(uart_port=0, baudrate=9600, apn="internet.apn", pwr_en_pin=2)
    sim.power_on(sim.pwr_en_pin)
    sim.toggle_lamp()
"""

from gsm_nbiot_lib.core.connection import ConnectionManager
from gsm_nbiot_lib.core.at_command import ATCommandInterface
from gsm_nbiot_lib.utils.helpers import save_state, load_state

class SIM7020(ConnectionManager):
    """
    A class for managing SIM7020 NB-IoT devices.

    Inherits from:
        ConnectionManager: Provides base functionality for power management,
        APN configuration, and signal quality checks.

    Attributes:
        pwr_en_pin (int): GPIO pin for enabling power.
        lampIsOn (int): State of the lamp (1 for on, 0 for off).

    Methods:
        - load_lamp_state(): Loads the lamp state from persistent storage.
        - save_lamp_state(): Saves the current lamp state to persistent storage.
        - toggle_lamp(): Toggles the lamp state and updates storage.
    """

    def __init__(self, uart_port, baudrate, apn, pwr_en_pin):
        """
        Initializes the SIM7020 manager.

        Args:
            uart_port (int): UART port number for communication.
            baudrate (int): Baud rate for UART communication.
            apn (str): APN string for network configuration.
            pwr_en_pin (int): GPIO pin number for power enable.
        """
        at_interface = ATCommandInterface(uart_port, baudrate)
        super().__init__(at_interface, apn)
        self.pwr_en_pin = pwr_en_pin
        self.load_lamp_state()

    def load_lamp_state(self):
        """
        Loads the lamp state from a database.

        Uses the `load_state` utility to retrieve the lamp's last saved state.
        Defaults to `1` (on) if no saved state is found.
        """
        loaded_state = load_state('state.db')
        self.lampIsOn = int(loaded_state) if loaded_state else 1

    def save_lamp_state(self):
        """
        Saves the current lamp state to a database.

        Uses the `save_state` utility to persist the lamp's state.
        """
        save_state('state.db', self.lampIsOn)

    def toggle_lamp(self):
        """
        Toggles the lamp state and updates persistent storage.

        Switches the `lampIsOn` attribute between 1 (on) and 0 (off).
        Also saves the new state using the `save_lamp_state` method.

        Notes:
            Add hardware-specific code here to control LEDs or other devices.
        """
        self.lampIsOn = 1 if self.lampIsOn == 0 else 0
        self.save_lamp_state()
        # Add code here for controlling LEDs or other hardware
