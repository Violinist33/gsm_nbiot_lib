from .sim7020 import SIM7020
from machine import UART
import time


class BlynkIntegration:
    """Class for integrating with the Blynk platform using the SIM7020 module."""

    def __init__(self, uart: UART, apn: str, blynk_token: str, baudrate: int = 9600, timeout: int = 1,
                 max_retries: int = 3):
        """
        Initializes Blynk integration with APN settings and access token.

        Args:
            uart (UART): UART object for SIM7020.
            apn (str): APN name for network connection.
            blynk_token (str): Access token for Blynk.
            baudrate (int, optional): UART connection speed. Defaults to 9600.
            timeout (int, optional): Response timeout in seconds. Defaults to 1.
            max_retries (int, optional): Maximum retries for data send/receive failures. Defaults to 3.
        """
        self.sim7020 = SIM7020(uart, baudrate, timeout)
        self.apn = apn
        self.blynk_token = blynk_token
        self.max_retries = max_retries
        self.connected = False  # Tracks connection status

    def log(self, level: str, message: str):
        """Simple logger to simulate a logging module."""
        print(f"[{level}] {message}")

    def connect(self):
        """
        Connects to the network and initializes the connection with Blynk.
        """
        try:
            self.sim7020.initialize()
            self.sim7020.set_apn(self.apn)
            self.sim7020.connect_network()
            self.connected = True
            self.log("INFO", "Connected to network and Blynk")
        except Exception as e:
            self.log("ERROR", f"Connection error: {e}")
            self.connected = False

    def ensure_connection(self):
        """
        Checks the connection and attempts reconnection if necessary.
        """
        if not self.connected:
            self.log("INFO", "Attempting reconnection...")
            self.connect()

    def send_value(self, virtual_pin: int, value: str):
        """
        Sends data to a specified virtual pin in Blynk.

        Args:
            virtual_pin (int): The virtual pin number in Blynk.
            value (str): The value to send.
        """
        self.ensure_connection()

        # Assumes the variable self.blynk_server_ip is defined
        # If not, it should be added to the configuration
        command = f'AT+HTTPGET="http://{self.sim7020.at_command.broker_address}/{self.blynk_token}/update/{virtual_pin}?value={value}"'
        for attempt in range(self.max_retries):
            try:
                self.sim7020.at_command.send_command(command, expected_response="OK")
                self.log("INFO", f"Value {value} sent to virtual pin {virtual_pin}")
                return
            except Exception as e:
                self.log("WARNING", f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        self.log("ERROR", f"Failed to send value to virtual pin {virtual_pin} after {self.max_retries} attempts")

    def get_value(self, virtual_pin: int):
        """
        Retrieves data from a specified virtual pin in Blynk.

        Args:
            virtual_pin (int): The virtual pin number in Blynk.

        Returns:
            str | None: The retrieved value, or None if an error occurred.
        """
        self.ensure_connection()

        # Similarly, assumes self.blynk_server_ip is defined
        command = f'AT+HTTPGET="http://{self.sim7020.at_command.broker_address}/{self.blynk_token}/get/{virtual_pin}"'
        for attempt in range(self.max_retries):
            try:
                response = self.sim7020.at_command.send_command(command, expected_response="OK")
                data = response[-1].split()[-1]  # Example of response parsing
                self.log("INFO", f"Retrieved value {data} from virtual pin {virtual_pin}")
                return data
            except Exception as e:
                self.log("WARNING", f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        self.log("ERROR", f"Failed to retrieve data from virtual pin {virtual_pin} after {self.max_retries} attempts")
        return None

    def disconnect(self):
        """
        Disconnects from Blynk and the NB-IoT network.
        """
        self.sim7020.disconnect_network()
        self.connected = False
        self.log("INFO", "Disconnected from Blynk and NB-IoT network")

    def close(self):
        """
        Closes the connection with the SIM7020 module.
        """
        self.sim7020.close()
        self.log("INFO", "Closed connection with SIM7020")
