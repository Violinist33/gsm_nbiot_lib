from .commands import ATCommand, ATCommandError


class SIM7020:
    """Class for controlling the SIM7020 module using AT commands."""

    def __init__(self, port: str, baudrate: int = 9600, timeout: int = 1):
        """
        Initializes the SIM7020 with the specified port and UART parameters.

        Args:
            port (str): UART port (e.g., "/dev/ttyUSB0" for Linux).
            baudrate (int, optional): Data transmission rate. Defaults to 9600.
            timeout (int, optional): Response timeout. Defaults to 1.
        """
        # Initializes ATCommand instance to manage commands with specified port, baudrate, and timeout
        self.at_command: ATCommand = ATCommand(port, baudrate, timeout)

    def initialize(self) -> None:
        """
        Performs the initial configuration of the module: checks the connection and sets initial parameters.

        Raises:
            ATCommandError: If connection to the SIM7020 module cannot be established.
        """
        # Checks connection status and raises ATCommandError if connection fails
        if not self.at_command.check_connection():
            raise ATCommandError("Failed to establish connection with SIM7020 module")

        print("SIM7020 module successfully connected")

    def set_apn(self, apn: str) -> None:
        """
        Sets the APN for network connection.

        Args:
            apn (str): APN name for the network.
        """
        # Sends APN configuration command
        self.at_command.set_apn(apn)
        print(f"APN '{apn}' successfully set")

    def connect_network(self) -> None:
        """
        Connects the module to the NB-IoT network.
        """
        # Sends network connection command
        self.at_command.connect_network()
        print("Network connection established")

    def disconnect_network(self) -> None:
        """
        Disconnects the module from the NB-IoT network.
        """
        # Sends network disconnection command
        self.at_command.disconnect_network()
        print("Network disconnection completed")

    def get_signal_quality(self) -> tuple[int, int]:
        """
        Retrieves the signal quality metrics from the module.

        Returns:
            tuple[int, int]: RSSI (Received Signal Strength Indicator) and BER (Bit Error Rate).
        """
        # Retrieves RSSI and BER values from the module
        rssi: int  # Received Signal Strength Indicator
        ber: int  # Bit Error Rate
        rssi, ber = self.at_command.get_signal_quality()
        print(f"Signal quality: RSSI={rssi}, BER={ber}")
        return rssi, ber

    def send_data(self, data: str) -> None:
        """
        Sends data through the module.

        Args:
            data (str): Data to be sent through the SIM7020 module.

        Raises:
            ATCommandError: If an error occurs during data transmission.
        """
        try:
            # Sends data transmission command with specified data
            self.at_command.send_command(f'AT+SEND={data}', expected_response="SEND OK")
            print("Data successfully sent")
        except ATCommandError:
            print("Error occurred while sending data")

    def close(self) -> None:
        """
        Terminates usage of the module and closes the UART connection.
        """
        # Closes the AT command interface and ends the connection
        self.at_command.close()
        print("Connection with the module closed")
