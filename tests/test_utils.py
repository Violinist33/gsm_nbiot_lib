# tests/test_utils.py

import unittest
from unittest.mock import patch, MagicMock
from sim7020py.utils import (
    parse_signal_quality,
    validate_response,
    parse_http_response,
    retry_operation,
    format_at_command,
    handle_timeout,
    extract_json_data,
)

class TestUtils(unittest.TestCase):

    def test_parse_signal_quality_success(self):
        """Test parse_signal_quality with a valid +CSQ response."""
        response = ["+CSQ: 15,99", "OK"]
        rssi, ber = parse_signal_quality(response)
        self.assertEqual(rssi, 15)
        self.assertEqual(ber, 99)

    def test_parse_signal_quality_failure(self):
        """Test parse_signal_quality with an invalid response format."""
        response = ["ERROR"]
        result = parse_signal_quality(response)
        self.assertIsNone(result)

    def test_validate_response_success(self):
        """Test validate_response when the expected keyword is found."""
        response = ["OK"]
        self.assertTrue(validate_response(response, expected_keyword="OK"))
    #
    # def test_validate_response_failure(self):
    #     """Test validate_response when the expected keyword is missing."""
    #     response = ["ERROR"]
    #     self.assertFalse(validate_response(response, expected_keyword="OK"))
    #
    def test_parse_http_response_success(self):
        """Test parse_http_response with a valid HTTP response."""
        response = ["Header: something", "Body data"]
        self.assertEqual(parse_http_response(response), "Body data")

    # def test_parse_http_response_failure(self):
    #     """Test parse_http_response with an empty response."""
    #     response = []
    #     self.assertIsNone(parse_http_response(response))

    def test_retry_operation_success(self):
        """Test retry_operation with a successful operation."""
        operation = MagicMock(return_value="Success")
        result = retry_operation(operation, max_retries=3, delay=0)
        self.assertEqual(result, "Success")
        operation.assert_called_once()

    # def test_retry_operation_failure(self):
    #     """Test retry_operation when the operation fails all retries."""
    #     operation = MagicMock(side_effect=Exception("Failure"))
    #     result = retry_operation(operation, max_retries=3, delay=0)
    #     self.assertIsNone(result)
    #     self.assertEqual(operation.call_count, 3)
    #
    def test_format_at_command_with_params(self):
        """Test format_at_command with parameters."""
        command = "AT+TEST"
        params = ["param1", "param2"]
        self.assertEqual(format_at_command(command, params), "AT+TEST=param1,param2")
    #
    def test_format_at_command_without_params(self):
        """Test format_at_command without parameters."""
        command = "AT+TEST"
        self.assertEqual(format_at_command(command), "AT+TEST")

    @patch('time.time', side_effect=[0, 1, 2, 3, 4, 5, 6])
    def test_handle_timeout_success(self, mock_time):
        """Test handle_timeout when the operation succeeds within the timeout."""
        operation = MagicMock(return_value="Success")
        result = handle_timeout(operation, timeout=5)
        self.assertEqual(result, "Success")
        operation.assert_called_once()
    #
    # @patch('time.time', side_effect=[0, 1, 2, 3, 4, 5, 6])
    # def test_handle_timeout_failure(self, mock_time):
    #     """Test handle_timeout when the operation exceeds the timeout."""
    #     operation = MagicMock(side_effect=Exception("Failure"))
    #     result = handle_timeout(operation, timeout=5)
    #     self.assertIsNone(result)
    #     self.assertGreaterEqual(operation.call_count, 5)
    #
    #
    # def test_extract_json_data_success(self):
    #     """Test extract_json_data with a valid JSON response."""
    #     response = ['{"key": "value"}']
    #     result = extract_json_data(response)
    #     self.assertEqual(result, {"key": "value"})
    #
    # def test_extract_json_data_failure(self):
    #     """Test extract_json_data with an invalid JSON response."""
    #     response = ["Invalid JSON"]
    #     result = extract_json_data(response)
    #     self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
