# gsm_nbiot_lib/core/command_parser.py

def parse_response(response):
    response = response.strip('\r\n')
    parts = response.split(': ', 1)
    command_name = parts[0].strip()
    parameters = []
    if len(parts) > 1:
        parameters = [param.strip().strip('"') for param in parts[1].split(',')]
    return command_name, parameters
