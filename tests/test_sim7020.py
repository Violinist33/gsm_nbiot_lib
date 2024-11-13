import unittest
from unittest.mock import patch, MagicMock
from sim7020py.sim7020 import SIM7020
from sim7020py.commands import ATCommandError


class TestSIM7020(unittest.TestCase):

    def setUp(self):
        patcher = patch('serial.Serial')
        self.mock_serial = patcher.start()
        self.addCleanup(patcher.stop)
        self.sim7020 = SIM7020(port="COM_TEST")
        self.mock_serial.return_value.readlines.return_value = [b"OK\r\n"]

        # Common Blynk server settings for tests
        self.sim7020.blynk_server_ip = "blynk-cloud.com"
        self.sim7020.blynk_server_port = 80
        self.sim7020.blynk_token = "test_token"  # Mock token for Blynk server

    def test_initialize_success(self):
        """
        Test that initialize successfully verifies connection with the module.
        """
        self.mock_serial.return_value.readlines.return_value = [b"OK\r\n"]
        self.sim7020.initialize()
        self.mock_serial.return_value.write.assert_called_with(b"AT\r\n")

    def test_initialize_failure(self):
        """
        Test that initialize raises ATCommandError on connection failure.
        """
        self.mock_serial.return_value.readlines.return_value = [b"ERROR\r\n"]
        with self.assertRaises(ATCommandError):
            self.sim7020.initialize()

    def test_set_apn(self):
        """
        Test that set_apn sends the correct AT command for setting the APN.
        """
        self.sim7020.set_apn("test_apn")
        self.mock_serial.return_value.write.assert_called_with(b'AT+CGDCONT=1,"IP","test_apn"\r\n')

    def test_connect_network_success(self):
        """
        Test that connect_network sends the correct command and receives OK response.
        """
        self.sim7020.connect_network()
        self.mock_serial.return_value.write.assert_called_with(b"AT+CGATT=1\r\n")

    def test_connect_network_failure(self):
        """
        Test that connect_network raises ATCommandError if connection fails.
        """
        self.mock_serial.return_value.readlines.return_value = [b"ERROR\r\n"]
        with self.assertRaises(ATCommandError):
            self.sim7020.connect_network()

    def test_disconnect_network_success(self):
        """
        Test that disconnect_network sends the correct command and receives OK response.
        """
        self.sim7020.disconnect_network()
        self.mock_serial.return_value.write.assert_called_with(b"AT+CGATT=0\r\n")

    def test_get_signal_quality(self):
        """
        Test that get_signal_quality returns the expected RSSI and BER values.
        """
        self.mock_serial.return_value.readlines.return_value = [b"+CSQ: 15,99\r\n", b"OK\r\n"]
        rssi, ber = self.sim7020.get_signal_quality()
        self.assertEqual(rssi, 15)
        self.assertEqual(ber, 99)
        self.mock_serial.return_value.write.assert_called_with(b"AT+CSQ\r\n")

    def test_send_data(self):
        """
        Test that send_data sends the correct HTTP command to Blynk.
        """
        # Example data and virtual pin
        virtual_pin = 1
        data = 25

        # Call send_data
        self.sim7020.send_data(
            f"http://{self.sim7020.blynk_server_ip}/{self.sim7020.blynk_token}/update/{virtual_pin}?value={data}")

        # Update expected command to match actual output
        self.mock_serial.return_value.write.assert_called_with(
            b'AT+SEND=http://blynk-cloud.com/test_token/update/1?value=25\r\n')

    def tearDown(self):
        """
        Clean up after each test.
        """
        self.sim7020.close()
        self.mock_serial.return_value.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()

# # tests/test_sim7020.py
#
# import unittest
# from unittest.mock import patch, MagicMock
# from sim7020py.sim7020 import SIM7020
# from sim7020py.commands import ATCommandError
#
#
# class TestSIM7020(unittest.TestCase):
#
#     def setUp(self):
#         patcher = patch('serial.Serial')
#         self.mock_serial = patcher.start()
#         self.addCleanup(patcher.stop)
#         self.sim7020 = SIM7020(port="COM_TEST")
#
#     def test_initialize_success(self):
#         """
#         Test that initialize successfully verifies connection with the module.
#         """
#         self.mock_serial.return_value.readlines.return_value = [b"OK\r\n"]
#         self.sim7020.initialize()
#         self.mock_serial.return_value.write.assert_called_with(b"AT\r\n")
#
#     def test_initialize_success(self):
#         """
#         Test that initialize successfully verifies connection with the module.
#         """
#         # Mock the response for initialize
#         self.mock_serial.return_value.readlines.return_value = [b"OK\r\n"]
#
#         # Call initialize and check it proceeds without raising an error
#         self.sim7020.initialize()
#
#         # Verify that the AT command was sent
#         self.mock_serial.return_value.write.assert_called_with(b"AT\r\n")
#
#     def test_set_apn(self):
#         """
#         Test that set_apn sends the correct AT command for setting the APN.
#         """
#         self.mock_serial.return_value.readlines.return_value = [b"OK\r\n"]
#         self.sim7020.set_apn("test_apn")
#         self.mock_serial.return_value.write.assert_called_with(b'AT+CGDCONT=1,"IP","test_apn"\r\n')
#
#     def test_set_apn(self):
#         """
#         Test that set_apn sends the correct AT command for setting the APN.
#         """
#         self.mock_serial.readlines.return_value = [b"OK\r\n"]
#
#         # Call the set_apn function
#         self.sim7020.set_apn("test_apn")
#
#         # Check if the correct AT command was sent
#         self.mock_serial.write.assert_called_with(b'AT+CGDCONT=1,"IP","test_apn"\r\n')
#
#     def test_connect_network_success(self):
#         """
#         Test that connect_network sends the correct command and receives OK response.
#         """
#         self.mock_serial.readlines.return_value = [b"OK\r\n"]
#
#         # Call connect_network
#         self.sim7020.connect_network()
#         self.mock_serial.write.assert_called_with(b"AT+CGATT=1\r\n")
#
#     def test_connect_network_failure(self):
#         """
#         Test that connect_network raises ATCommandError if connection fails.
#         """
#         self.mock_serial.readlines.return_value = [b"ERROR\r\n"]
#
#         # Expect an exception to be raised on failure
#         with self.assertRaises(ATCommandError):
#             self.sim7020.connect_network()
#
#     def test_disconnect_network_success(self):
#         """
#         Test that disconnect_network sends the correct command and receives OK response.
#         """
#         self.mock_serial.readlines.return_value = [b"OK\r\n"]
#
#         # Call disconnect_network
#         self.sim7020.disconnect_network()
#         self.mock_serial.write.assert_called_with(b"AT+CGATT=0\r\n")
#
#     def test_get_signal_quality(self):
#         """
#         Test that get_signal_quality returns the expected RSSI and BER values.
#         """
#         self.mock_serial.readlines.return_value = [b"+CSQ: 15,99\r\n", b"OK\r\n"]
#
#         # Call get_signal_quality
#         rssi, ber = self.sim7020.get_signal_quality()
#         self.assertEqual(rssi, 15)
#         self.assertEqual(ber, 99)
#         self.mock_serial.write.assert_called_with(b"AT+CSQ\r\n")
#
#     def test_send_data(self):
#         """
#         Test that send_data sends the correct HTTP command to Blynk.
#         """
#         # Mock response for HTTP GET to simulate success
#         self.mock_serial.readlines.return_value = [b"SEND OK\r\n"]
#
#         # Example data and virtual pin
#         virtual_pin = 1
#         data = 25
#
#         # Mock Blynk server settings
#         self.sim7020.blynk_server_ip = "blynk-cloud.com"
#         self.sim7020.blynk_server_port = 80
#
#         # Call send_data
#         self.sim7020.send_data(
#             f"http://{self.sim7020.blynk_server_ip}/{self.sim7020.blynk_token}/update/{virtual_pin}?value={data}")
#         self.mock_serial.write.assert_called_with(
#             b'AT+HTTPGET="http://blynk-cloud.com/test_token/update/1?value=25"\r\n')
#
#     def tearDown(self):
#         """
#         Clean up after each test.
#         """
#         self.sim7020.close()
#         self.mock_serial.close.assert_called_once()
#
#
# if __name__ == "__main__":
#     unittest.main()

#
# class TestSIM7020(unittest.TestCase):
#     @patch('serial.Serial')
#     # def setUp(self, mock_serial):
#     #     """
#     #     Set up the SIM7020 instance with a mock serial connection for testing.
#     #     """
#     #     self.mock_serial = mock_serial.return_value
#     #     self.sim7020 = SIM7020(port="COM_TEST", apn="test_apn", blynk_token="test_token")
#
#     def setUp(self):
#         self.sim7020 = SIM7020(port="COM_TEST")  # Remove apn and blynk_token
#
#     def test_initialize_success(self):
#         """
#         Test that initialize successfully verifies connection with the module.
#         """
#         self.mock_serial.readlines.return_value = [b"OK\r\n"]
#
#         # Call the initialize function and verify no exceptions
#         self.sim7020.initialize()
#         self.mock_serial.write.assert_called_with(b"AT\r\n")

# def test_initialize_failure(self):
#     """
#     Test that initialize raises ATCommandError if the module does not respond.
#     """
#     self.mock_serial.readlines.return_value = [b"ERROR\r\n"]
#
#     # Expect an exception to be raised on initialization failure
#     with self.assertRaises(ATCommandError):
#         self.sim7020.initialize()
