# src/gsm_serial_lib/blynk_integration.py
# sim7020py/blynk_integration.py

from .sim7020 import SIM7020
import time
import logging

logging.basicConfig(level=logging.INFO)


class BlynkIntegration:
    """Class for integration with the Blynk platform via SIM7020."""

    def __init__(self, port, apn, blynk_token, baudrate=9600, timeout=1, max_retries=3):
        """
        Initializes Blynk integration with APN and token settings.

        :param port: UART port for SIM7020 (e.g., "/dev/ttyUSB0" for Linux)
        :param apn: APN name for network connection
        :param blynk_token: Access token for Blynk
        :param baudrate: Baud rate for UART communication
        :param timeout: Timeout for response wait
        :param max_retries: Maximum retry attempts on data send/receive failure
        """
        self.sim7020 = SIM7020(port, baudrate, timeout)
        self.apn = apn
        self.blynk_token = blynk_token
        self.max_retries = max_retries
        self.connected = False

    def connect(self):
        """
        Connects to the network and initializes the Blynk connection.
        """
        try:
            self.sim7020.initialize()
            self.sim7020.set_apn(self.apn)
            self.sim7020.connect_network()
            self.connected = True
            logging.info("Connected to network and Blynk")
        except Exception as e:
            logging.error(f"Connection error: {e}")
            self.connected = False

    def ensure_connection(self):
        """
        Checks the connection and attempts to reconnect if necessary.
        """
        if not self.connected:
            logging.info("Attempting reconnection...")
            self.connect()

    def send_value(self, virtual_pin, value):
        """
        Sends data to a specified virtual pin on the Blynk server.

        :param virtual_pin: Virtual pin number on Blynk
        :param value: Value to be sent
        """
        self.ensure_connection()

        command = f"AT+HTTPGET=\"http://{self.blynk_server_ip}/{self.blynk_token}/update/{virtual_pin}?value={value}\""
        for attempt in range(self.max_retries):
            try:
                self.sim7020.at_command.send_command(command, expected_response="OK")
                logging.info(f"Value {value} sent to virtual pin {virtual_pin}")
                return
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)  # Small pause before retrying

        logging.error(f"Failed to send value to virtual pin {virtual_pin} after {self.max_retries} attempts")

    def get_value(self, virtual_pin):
        """
        Retrieves data from a specified virtual pin on the Blynk server.

        :param virtual_pin: Virtual pin number on Blynk
        :return: Retrieved value or None if an error occurs
        """
        self.ensure_connection()

        command = f"AT+HTTPGET=\"http://{self.blynk_server_ip}/{self.blynk_token}/get/{virtual_pin}\""
        for attempt in range(self.max_retries):
            try:
                response = self.sim7020.at_command.send_command(command, expected_response="OK")
                data = response[-1].split()[-1]  # Example response parsing
                logging.info(f"Retrieved value {data} from virtual pin {virtual_pin}")
                return data
            except Exception as e:
                logging.warning(f"Attempt {attempt + 1} failed: {e}")
                time.sleep(1)

        logging.error(f"Failed to retrieve data from virtual pin {virtual_pin} after {self.max_retries} attempts")
        return None

    def disconnect(self):
        """
        Disconnects from Blynk and NB-IoT network.
        """
        self.sim7020.disconnect_network()
        self.connected = False
        logging.info("Disconnected from Blynk and NB-IoT network")

    def close(self):
        """
        Closes the connection with the SIM7020 module.
        """
        self.sim7020.close()
        logging.info("Closed connection with SIM7020")
