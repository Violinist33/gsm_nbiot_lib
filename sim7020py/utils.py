import logging
import time
# import binascii

logging.basicConfig(level=logging.INFO)

def save_state(filename, variable, mode='w'):
    """
        @brief Saves the value of a variable to a file.

        @param filename The name of the file to save the variable to.
        @param variable The variable whose value is to be saved.
        @param mode (optional) The mode to open the file in. Defaults to 'w' (write mode).

        This function writes the string representation of a variable to a specified file.
    """
    with open(filename, mode) as f:
        f.write(str(variable))


def load_state(filename):
    """
     * @brief Reads a variable's value from a file.
     *
     * @param filename The name of the file to read the variable from.
     * @return The content read from the file. If the file does not exist, a default value of 0 is saved to the file and returned.
     *
     * This function attempts to read a variable's value from the specified file. If the file does not exist,
     * it creates the file with a default value of 0.
    """
    try:
        with open(filename, 'r') as f:
            return f.read()
    except OSError:
        save_state(filename, 0)
        return 0


def parse_response(response):
    """
     * @brief Parses the response from AT command strings.
     *
     * @param response The raw response string from an AT command.
     * @return A tuple containing the command name and a list of parameters.
     *
     * This function cleans and splits an AT command response to extract the command name and parameters. The
     * command name is extracted before the first ": ", and parameters are split by commas.
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


# def hexStr_to_str(hex_str):
#     """
#      * @brief Converts a hexadecimal string to a regular string.
#      *
#      * @param hex_str The hexadecimal string to convert.
#      * @return The decoded regular string.
#      *
#      * This function converts a given hexadecimal string into its equivalent regular string format.
#      """
#     hex_data = hex_str.encode('utf-8')
#     str_bin = binascii.unhexlify(hex_data)
#     return str_bin.decode('utf-8')



def parse_signal_quality(response):
    """
    Parses the response from the AT+CSQ command to retrieve signal quality.

    :param response: The response from the AT+CSQ command
    :return: Tuple (RSSI, BER) if successful, or None if parsing fails
    """
    try:
        for line in response:
            if line.startswith("+CSQ:"):
                _, signal_info = line.split(": ")
                rssi, ber = signal_info.split(",")
                return int(rssi), int(ber)
    except (ValueError, IndexError) as e:
        logging.error(f"Error parsing signal quality: {e}")

    return None


def validate_response(response, expected_keyword="OK"):
    """
    Checks if the response contains an expected keyword, typically to confirm a command succeeded.

    :param response: The response received from the module
    :param expected_keyword: The keyword expected in the response (default is "OK")
    :return: True if the keyword is found, False otherwise
    """
    if any(expected_keyword in line for line in response):
        return True
    else:
        logging.warning(f"Expected keyword '{expected_keyword}' not found in response: {response}")
        return False


def parse_http_response(response):
    """
    Parses the HTTP response from Blynk or other servers, returning useful data.

    :param response: The HTTP response from the AT+HTTPGET or AT+HTTPPOST command
    :return: Useful data from the response, or None if parsing fails
    """
    try:
        # Assume the useful data is in the last line of the response
        data = response[-1].strip()
        return data
    except IndexError as e:
        logging.error(f"Error parsing HTTP response: {e}")
        return None


def retry_operation(operation, max_retries=3, delay=1):
    """
    Retries an operation several times in case of failure.

    :param operation: A function or lambda expression to execute
    :param max_retries: The maximum number of retry attempts
    :param delay: Delay between attempts (in seconds)
    :return: Result of the operation if successful, or None if all retries fail
    """
    for attempt in range(max_retries):
        try:
            result = operation()
            return result
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay)
    logging.error("Operation failed after all retry attempts")
    return None


def format_at_command(command, params=None):
    """
    Formats an AT command with optional parameters.

    :param command: The base AT command (e.g., "AT+CSQ")
    :param params: Parameters to append to the command (optional)
    :return: Formatted AT command string
    """
    if params:
        return f"{command}={','.join(map(str, params))}"
    return command


def handle_timeout(operation, timeout=5):
    """
    Executes an operation with a specified timeout.

    :param operation: Function to execute
    :param timeout: Time limit for the operation (in seconds)
    :return: Result of the operation if successful within timeout, or None if timeout occurs
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            result = operation()
            return result
        except Exception as e:
            logging.warning(f"Operation failed, retrying within timeout: {e}")
            time.sleep(0.5)
    logging.error("Operation timed out")
    return None


def extract_json_data(response):
    """
    Attempts to extract JSON-formatted data from an HTTP response string.

    :param response: The HTTP response from the module
    :return: Parsed JSON data as a dictionary, or None if extraction fails
    """
    import json
    try:
        data = json.loads(response[-1])  # Assuming JSON is in the last line
        return data
    except (json.JSONDecodeError, IndexError) as e:
        logging.error(f"Error parsing JSON data: {e}")
        return None

