# tests/test_commands.py

import unittest
from unittest.mock import MagicMock, patch
from sim7020py.commands import ATCommand, ATCommandError


class TestATCommand(unittest.TestCase):
    @patch('serial.Serial')
    def setUp(self, mock_serial):
        """
        Set up the ATCommand instance with a mock serial connection for testing.
        """
        self.mock_serial = mock_serial.return_value
        self.at_command = ATCommand(port="COM_TEST")

    def test_send_command_success(self):
        """
        Test that send_command successfully sends an AT command and receives the expected response.
        """
        # Mock the response from the serial port
        self.mock_serial.readlines.return_value = [b"OK\r\n"]

        # Test the command
        response = self.at_command.send_command("AT")
        self.assertIn("OK", response)
        self.mock_serial.write.assert_called_with(b"AT\r\n")

    def test_send_command_failure(self):
        """
        Test that send_command raises ATCommandError if the expected response is not received.
        """
        # Mock a different response to simulate a failure
        self.mock_serial.readlines.return_value = [b"ERROR\r\n"]

        # Test that an error is raised
        with self.assertRaises(ATCommandError):
            self.at_command.send_command("AT", expected_response="OK")

    def test_check_connection_success(self):
        """
        Test that check_connection returns True if the module responds with 'OK'.
        """
        # Mock the response to simulate a successful connection check
        self.mock_serial.readlines.return_value = [b"OK\r\n"]
        self.assertTrue(self.at_command.check_connection())

    def test_check_connection_failure(self):
        """
        Test that check_connection returns False if the module does not respond with 'OK'.
        """
        # Mock the response to simulate a failed connection check
        self.mock_serial.readlines.return_value = [b"ERROR\r\n"]
        self.assertFalse(self.at_command.check_connection())

    def test_get_signal_quality(self):
        """
        Test that get_signal_quality returns the expected RSSI and BER values.
        """
        # Mock the response for the AT+CSQ command
        self.mock_serial.readlines.return_value = [b"+CSQ: 15,99\r\n", b"OK\r\n"]

        # Test the command
        rssi, ber = self.at_command.get_signal_quality()
        self.assertEqual(rssi, 15)
        self.assertEqual(ber, 99)
        self.mock_serial.write.assert_called_with(b"AT+CSQ\r\n")

    def test_set_apn(self):
        """
        Test that set_apn sends the correct AT command for setting the APN.
        """
        # Mock the response from the serial port to include "OK" to simulate success
        self.mock_serial.readlines.return_value = [b"OK\r\n"]

        # Call the set_apn function
        self.at_command.set_apn("test_apn")

        # Check if the correct AT command was sent
        self.mock_serial.write.assert_called_with(b'AT+CGDCONT=1,"IP","test_apn"\r\n')

    def test_connect_network(self):
        """
        Test that connect_network sends the correct AT command for network attachment.
        """
        # Mock the response for network attachment
        self.mock_serial.readlines.return_value = [b"OK\r\n"]

        # Test the command
        self.at_command.connect_network()
        self.mock_serial.write.assert_called_with(b"AT+CGATT=1\r\n")

    def test_disconnect_network(self):
        """
        Test that disconnect_network sends the correct AT command for network detachment.
        """
        # Mock the response for network detachment
        self.mock_serial.readlines.return_value = [b"OK\r\n"]

        # Test the command
        self.at_command.disconnect_network()
        self.mock_serial.write.assert_called_with(b"AT+CGATT=0\r\n")

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.at_command.close()
        self.mock_serial.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
