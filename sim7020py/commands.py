import time
import serial  # Assumes the PySerial library is used for UART communication

class ATCommandError(Exception):
    """Exception for AT command errors."""
    pass

class ATCommand:
    """Class for sending and handling AT commands to the SIM7020 module over UART."""

    def __init__(self, port, baudrate=9600, timeout=1):
        """
        Initializes the connection to the module via UART.

        :param port: UART port (e.g., "/dev/ttyUSB0" for Linux)
        :param baudrate: Data transmission rate
        :param timeout: Response timeout
        """
        self.serial = serial.Serial(port, baudrate, timeout=timeout)

    def send_command(self, command, expected_response="OK", delay=0.5):
        """
        Sends an AT command and waits for a response.

        :param command: The AT command to send
        :param expected_response: Expected response (default is "OK")
        :param delay: Delay before reading the response
        :return: Response from the module
        """
        # Clear the buffer and send the command
        self.serial.reset_input_buffer()
        self.serial.write((command + "\r\n").encode())

        time.sleep(delay)
        response = self.serial.readlines()

        # Convert bytes to strings and remove extra characters
        response = [line.decode().strip() for line in response]

        # Check for the expected response
        if expected_response not in response:
            raise ATCommandError(f"Failed to receive expected response: {expected_response}")

        return response

    def check_connection(self):
        """
        Checks the connection with the module using the AT command.

        :return: True if the module responds, otherwise False
        """
        try:
            response = self.send_command("AT")
            return "OK" in response
        except ATCommandError:
            return False

    def get_signal_quality(self):
        """
        Requests the signal quality from the module (AT+CSQ command).

        :return: Signal quality (includes RSSI and BER)
        """
        response = self.send_command("AT+CSQ")

        # Expected response format: "+CSQ: <rssi>,<ber>"
        for line in response:
            if line.startswith("+CSQ:"):
                _, signal_info = line.split(": ")
                rssi, ber = signal_info.split(",")
                return int(rssi), int(ber)

        raise ATCommandError("Failed to retrieve signal quality")

    def set_apn(self, apn):
        """
        Sets the APN (Access Point Name) for network connection.

        :param apn: APN name
        :return: None
        """
        self.send_command(f'AT+CGDCONT=1,"IP","{apn}"')

    def connect_network(self):
        """
        Connects to the network (AT+CGATT=1 command).

        :return: None
        """
        self.send_command("AT+CGATT=1")

    def disconnect_network(self):
        """
        Disconnects from the network (AT+CGATT=0 command).

        :return: None
        """
        self.send_command("AT+CGATT=0")

    def close(self):
        """
        Closes the UART connection.
        """
        self.serial.close()