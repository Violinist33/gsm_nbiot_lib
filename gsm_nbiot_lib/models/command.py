"""
Module for handling and logging AT command responses.

This module provides a utility function to log and display information about
AT command responses, including the command name and its parameters.

Functions:
    - info_cmd(command_name, parameters): Logs and displays information about the command.

Example Usage:
    info_cmd("+CSQ", ["15", "99"])
"""

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
    if command_name == "ERROR":
        print("Error occurred while executing the command")
    print("Command name:", command_name)
    print("Parameters:", parameters, "\n")
