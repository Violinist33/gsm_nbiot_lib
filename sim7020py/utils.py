import time
import json

def log(level, message):
    """Simple logging function for MicroPython."""
    print(f"[{level}] {message}")

def save_state(filename, variable, mode='w'):
    """
    Saves the value of a variable to a file.

    Args:
        filename (str): The name of the file to save the variable to.
        variable (Any): The variable whose value is to be saved.
        mode (str): The mode to open the file in. Defaults to 'w' (write mode).
    """
    with open(filename, mode) as f:
        f.write(str(variable))

def load_state(filename):
    """
    Reads a variable's value from a file.

    Args:
        filename (str): The name of the file to read the variable from.

    Returns:
        str | int: The content read from the file. If the file does not exist, a default value of 0 is saved to the file and returned.
    """
    try:
        with open(filename, 'r') as f:
            content = f.read()
            return content
    except OSError:
        save_state(filename, 0)
        return 0

def parse_response(response):
    """
    Parses the response from AT command strings.

    Args:
        response (str): The raw response string from an AT command.

    Returns:
        tuple: A tuple containing the command name and a list of parameters.
    """
    response = response.strip('\r\n')
    lines = response.split('\r\n')
    parts = lines[0].split(': ')
    command_name = parts[0].strip(' ')
    parameters = [""]
    if len(parts) > 1:
        parts[1] = parts[1].strip('\r\n')
        parameters = parts[1].split(',')
    return command_name, parameters

def parse_signal_quality(response):
    """
    Parses the response from the AT+CSQ command to retrieve signal quality.

    Args:
        response (list): The response from the AT+CSQ command.

    Returns:
        tuple | None: Tuple (RSSI, BER) if successful, or None if parsing fails.
    """
    try:
        for line in response:
            if line.startswith("+CSQ:"):
                _, signal_info = line.split(": ")
                rssi, ber = map(int, signal_info.split(","))
                return rssi, ber
    except (ValueError, IndexError) as e:
        log("ERROR", f"Error parsing signal quality: {e}")

    return None

def validate_response(response, expected_keyword="OK"):
    """
    Checks if the response contains an expected keyword, typically to confirm a command succeeded.

    Args:
        response (list): The response received from the module.
        expected_keyword (str): The keyword expected in the response. Defaults to "OK".

    Returns:
        bool: True if the keyword is found, False otherwise.
    """
    if any(expected_keyword in line for line in response):
        return True
    else:
        log("WARNING", f"Expected keyword '{expected_keyword}' not found in response: {response}")
        return False

def parse_http_response(response):
    """
    Parses the HTTP response from Blynk or other servers, returning useful data.

    Args:
        response (list): The HTTP response from the AT+HTTPGET or AT+HTTPPOST command.

    Returns:
        str | None: Useful data from the response, or None if parsing fails.
    """
    try:
        data = response[-1].strip()
        return data
    except IndexError as e:
        log("ERROR", f"Error parsing HTTP response: {e}")
        return None

def retry_operation(operation, max_retries=3, delay=1):
    """
    Retries an operation several times in case of failure.

    Args:
        operation (Callable): A function or lambda expression to execute.
        max_retries (int): The maximum number of retry attempts. Defaults to 3.
        delay (int): Delay between attempts (in seconds). Defaults to 1.

    Returns:
        Any | None: Result of the operation if successful, or None if all retries fail.
    """
    for attempt in range(max_retries):
        try:
            result = operation()
            return result
        except Exception as e:
            log("WARNING", f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    log("ERROR", "Operation failed after all retry attempts")
    return None

def format_at_command(command, params=None):
    """
    Formats an AT command with optional parameters.

    Args:
        command (str): The base AT command (e.g., "AT+CSQ").
        params (list | None): Parameters to append to the command.

    Returns:
        str: Formatted AT command string.
    """
    if params:
        return f"{command}={','.join(map(str, params))}"
    return command

def handle_timeout(operation, timeout=5):
    """
    Executes an operation with a specified timeout.

    Args:
        operation (Callable): Function to execute.
        timeout (int): Time limit for the operation (in seconds). Defaults to 5.

    Returns:
        Any | None: Result of the operation if successful within timeout, or None if timeout occurs.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = operation()
            return result
        except Exception as e:
            log("WARNING", f"Operation failed, retrying within timeout: {e}")
            time.sleep(0.5)
    log("ERROR", "Operation timed out")
    return None

def extract_json_data(response):
    """
    Attempts to extract JSON-formatted data from an HTTP response string.

    Args:
        response (list): The HTTP response from the module.

    Returns:
        dict | None: Parsed JSON data as a dictionary, or None if extraction fails.
    """
    try:
        data = json.loads(response[-1])  # Assuming JSON is in the last line
        return data
    except (json.JSONDecodeError, IndexError) as e:
        log("ERROR", f"Error parsing JSON data: {e}")
        return None
