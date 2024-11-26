"""
Module for custom exceptions used in the GSM NB-IoT library.

This module defines custom exception classes for handling errors related to
AT commands and connection issues.

Classes:
    - ATCommandError: Raised when an AT command fails or returns an error.
    - ConnectionError: Raised for errors related to connection issues.

Example Usage:
    raise ATCommandError("Invalid response from AT command")
    raise ConnectionError("Failed to establish a connection")
"""

class ATCommandError(Exception):
    """
    Exception for AT command errors.

    This exception is raised when an AT command fails, returns an error, or
    provides an invalid response.

    Example:
        raise ATCommandError("AT+CSQ failed with ERROR")
    """
    pass


class ConnectionError(Exception):
    """
    Exception for connection-related errors.

    This exception is raised when the device fails to establish or maintain
    a connection.

    Example:
        raise ConnectionError("Network attachment failed")
    """
    pass
