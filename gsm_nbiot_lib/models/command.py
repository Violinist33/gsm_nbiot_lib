# gsm_nbiot_lib/models/command.py

def info_cmd(command_name, parameters):
    """
    Logs and displays information about an AT command response.

    Args:
        command_name (str): The name of the command or response identifier.
        parameters (list): A list of parameters associated with the command.

    Behavior:
        - If the command name is "ERROR", a specific error message is printed.
        - Otherwise, logs the command name and parameters to the console.

    Example:
        info_cmd("+CSQ", ["15", "99"])
        Output:
            Command name: +CSQ
            Parameters: ['15', '99']

        info_cmd("ERROR", [])
        Output:
            Error occurred while executing the command
    """

    if parameters:
        print("Command name:", command_name)
        print("Parameters:", parameters, "\n")

    if command_name == "ERROR":
        print("Error occurred while executing the command")


def log_command_execution(command, status):
    """
    Logs the execution status of a command.

    Args:
        command (str): The AT command that was executed.
        status (str): The status of the command execution (e.g., "Success", "Failed").

    Behavior:
        - Logs the command and its execution status to the console.

    Example:
        log_command_execution("AT+CFUN=1", "Success")
        Output:
            Command: AT+CFUN=1 executed successfully.
    """
    pass


def validate_command_response(command, response):
    """
    Validates the response received from an executed AT command.

    Args:
        command (str): The AT command that was executed.
        response (str): The response received from the device.

    Returns:
        bool: True if the response is valid and indicates success, False otherwise.

    Behavior:
        - Checks if the response contains "OK".
        - Logs appropriate messages based on the response content.

    Example:
        is_valid = validate_command_response("AT+CSQ", "OK\r\n")
        # is_valid == True
    """
    pass
