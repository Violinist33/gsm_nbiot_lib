import logging
import time
import json
from typing import Callable, Any

logging.basicConfig(level=logging.INFO)


def save_state(filename: str, variable: Any, mode: str = 'w') -> None:
    """
    Saves the value of a variable to a file.

    Args:
        filename (str): The name of the file to save the variable to.
        variable (Any): The variable whose value is to be saved.
        mode (str): The mode to open the file in. Defaults to 'w' (write mode).
    """
    with open(filename, mode) as f:
        f.write(str(variable))


def load_state(filename: str) -> str | int:
    """
    Reads a variable's value from a file.

    Args:
        filename (str): The name of the file to read the variable from.

    Returns:
        str | int: The content read from the file. If the file does not exist, a default value of 0 is saved to the file and returned.
    """
    try:
        with open(filename, 'r') as f:
            content: str = f.read()
            return content
    except OSError:
        save_state(filename, 0)
        return 0


def parse_response(response: str) -> tuple[str, list[str]]:
    """
    Parses the response from AT command strings.

    Args:
        response (str): The raw response string from an AT command.

    Returns:
        tuple[str, list[str]]: A tuple containing the command name and a list of parameters.
    """
    response = response.strip('\r\n')
    lines: list[str] = response.split('\r\n')
    parts: list[str] = lines[0].split(': ')
    command_name: str = parts[0].strip(' ')
    parameters: list[str] = [""]
    if len(parts) > 1:
        parts[1] = parts[1].strip('\r\n')
        parameters = parts[1].split(',')
    return command_name, parameters


def parse_signal_quality(response: list[str]) -> tuple[int, int] | None:
    """
    Parses the response from the AT+CSQ command to retrieve signal quality.

    Args:
        response (list[str]): The response from the AT+CSQ command.

    Returns:
        tuple[int, int] | None: Tuple (RSSI, BER) if successful, or None if parsing fails.
    """
    try:
        for line in response:
            if line.startswith("+CSQ:"):
                _, signal_info = line.split(": ")
                rssi, ber = map(int, signal_info.split(","))
                return rssi, ber
    except (ValueError, IndexError) as e:
        logging.error(f"Error parsing signal quality: {e}")

    return None


def validate_response(response: list[str], expected_keyword: str = "OK") -> bool:
    """
    Checks if the response contains an expected keyword, typically to confirm a command succeeded.

    Args:
        response (list[str]): The response received from the module.
        expected_keyword (str): The keyword expected in the response. Defaults to "OK".

    Returns:
        bool: True if the keyword is found, False otherwise.
    """
    if any(expected_keyword in line for line in response):
        return True
    else:
        logging.warning(f"Expected keyword '{expected_keyword}' not found in response: {response}")
        return False


def parse_http_response(response: list[str]) -> str | None:
    """
    Parses the HTTP response from Blynk or other servers, returning useful data.

    Args:
        response (list[str]): The HTTP response from the AT+HTTPGET or AT+HTTPPOST command.

    Returns:
        str | None: Useful data from the response, or None if parsing fails.
    """
    try:
        data: str = response[-1].strip()
        return data
    except IndexError as e:
        logging.error(f"Error parsing HTTP response: {e}")
        return None


def retry_operation(operation: Callable[[], Any], max_retries: int = 3, delay: int = 1) -> Any | None:
    """
    Retries an operation several times in case of failure.

    Args:
        operation (Callable[[], Any]): A function or lambda expression to execute.
        max_retries (int): The maximum number of retry attempts. Defaults to 3.
        delay (int): Delay between attempts (in seconds). Defaults to 1.

    Returns:
        Any | None: Result of the operation if successful, or None if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            result: Any = operation()
            return result
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    logging.error("Operation failed after all retry attempts")
    return None


def format_at_command(command: str, params: list[str] | None = None) -> str:
    """
    Formats an AT command with optional parameters.

    Args:
        command (str): The base AT command (e.g., "AT+CSQ").
        params (list[str] | None): Parameters to append to the command.

    Returns:
        str: Formatted AT command string.
    """
    if params:
        return f"{command}={','.join(map(str, params))}"
    return command


def handle_timeout(operation: Callable[[], Any], timeout: int = 5) -> Any | None:
    """
    Executes an operation with a specified timeout.

    Args:
        operation (Callable[[], Any]): Function to execute.
        timeout (int): Time limit for the operation (in seconds). Defaults to 5.

    Returns:
        Any | None: Result of the operation if successful within timeout, or None if timeout occurs.
    """
    start_time: float = time.time()
    while time.time() - start_time < timeout:
        try:
            result: Any = operation()
            return result
        except Exception as e:
            logging.warning(f"Operation failed, retrying within timeout: {e}")
            time.sleep(0.5)
    logging.error("Operation timed out")
    return None


def extract_json_data(response: list[str]) -> dict | None:
    """
    Attempts to extract JSON-formatted data from an HTTP response string.

    Args:
        response (list[str]): The HTTP response from the module.

    Returns:
        dict | None: Parsed JSON data as a dictionary, or None if extraction fails.
    """
    try:
        data: dict = json.loads(response[-1])  # Assuming JSON is in the last line
        return data
    except (json.JSONDecodeError, IndexError) as e:
        logging.error(f"Error parsing JSON data: {e}")
        return None
