# gsm_nbiot_lib

> Open-source MicroPython library for GSM NB-IoT modules with high-level AT-command abstraction, MQTT and Blynk integrations, and structured error handling.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![MicroPython](https://img.shields.io/badge/MicroPython-1.22+-green.svg)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Poetry](https://img.shields.io/badge/poetry-1.2+-blue.svg)
![Hardware](https://img.shields.io/badge/hardware-Raspberry%20Pi%20Pico-red.svg)
![Module](https://img.shields.io/badge/module-SIM7020E-orange.svg)
[![DOI](https://img.shields.io/badge/DOI-10.3390%2Fs25175322-blue.svg)](https://doi.org/10.3390/s25175322)

## Overview

`gsm_nbiot_lib` is a modular, object-oriented MicroPython library that abstracts AT-command handling for GSM NB-IoT modules. It automates network configuration, supports protocols such as MQTT and Blynk, and provides typed exceptions with bounded retries and timeouts for predictable error handling on resource-constrained microcontrollers.

The library was developed and validated on a **Raspberry Pi Pico** paired with a **SIMCom SIM7020E** module. Empirical benchmarks across three canonical IoT tasks demonstrated a **64.1% reduction in handwritten code** and an **81.1% reduction in time to first successful run** compared to manual AT-command control.

The library is described in detail in the peer-reviewed article published in *Sensors* (MDPI, 2025): [Model of an Open-Source MicroPython Library for GSM NB-IoT](https://doi.org/10.3390/s25175322).

## Key Features

- **High-level GSM module control.** Send AT commands, configure APN, manage network attachment, and read signal quality through clean Python methods rather than raw command strings.
- **MQTT integration.** Built-in support for `AT+CMQNEW`, `AT+CMQCON`, `AT+CMQPUB`, and `AT+CMQSUB` with automatic HEX payload conversion.
- **Blynk integration.** Send and read virtual pin values via HTTP GET with automatic reconnection logic.
- **Structured error handling.** Typed exceptions (`ATCommandError`) with bounded retries and per-command timeouts prevent hangs under unstable signal conditions.
- **State persistence.** Save and restore device state across reboots using `save_state` / `load_state` helpers.
- **Power management.** Light-sleep and deep-sleep helpers for battery-powered deployments.
- **Hardware-agnostic core.** Adapter-style architecture allows new module drivers (SIM7000, Quectel BC95) to be added without modifying the core.
- **Testable without hardware.** All core components can be unit-tested with `unittest.mock` simulating UART responses.

## How It Compares

| Feature | gsm_nbiot_lib | tmshlvck/micropython-sim7000 | Datacake/micropython-cellular-wrapper |
|---|---|---|---|
| Architecture | Modular, object-oriented, layered | Monolithic / script-based driver | High-level, single-purpose wrapper |
| High-level protocols | MQTT implemented, Blynk integrated, HTTP supported | Basic AT helpers, manual protocol code | Datacake-only |
| Module extensibility | Adapter pattern, easy to extend | Tightly coupled to SIM7000 | Tightly coupled to one platform |
| Error handling | Typed exceptions (`ATCommandError`), bounded retries | Boolean returns | Platform-dependent |
| Primary use case | Scalable IoT prototyping with multiple services | Basic SIM7000 connectivity | Datacake cloud ingestion |

## Performance

Measured on Raspberry Pi Pico with SIM7020E (Vodafone NB-IoT, RSSI -85 to -95 dBm), averaged over 50 iterations:

| Operation | Average Time | Peak Memory | Notes |
|---|---:|---:|---|
| `power_on()` | 1450 ± 50 ms | 256 ± 16 B | Module power-up to ready signal |
| `connect_network()` | 8200 ± 350 ms | 512 ± 32 B | Full NB-IoT registration sequence |
| `get_signal_quality()` | 240 ± 25 ms | 128 ± 8 B | `AT+CSQ` query and parse |
| `mqtt.publish()` | 380 ± 40 ms | 480 ± 24 B | Send payload + broker ack |

### Development Effort Reduction

Benchmarked across three canonical IoT tasks (network init, MQTT publish, error handling):

| Task | Lines of Code Reduction | Implementation Time Reduction |
|---|---:|---:|
| A. Network initialization | -71.4% | -80.0% |
| B. MQTT data transmission | -70.8% | -80.0% |
| C. Error handling | -50.0% | -83.3% |
| **Average** | **-64.1%** | **-81.1%** |

Full benchmark scripts (paired manual vs library implementations) are available under [`code_examples_for_benchmarking/`](./code_examples_for_benchmarking).

## Architecture

The library follows a layered, hardware-agnostic design:

```
gsm_nbiot_lib/
├── core/              # AT command interface, connection manager, parser, exceptions
├── modules/           # Device-specific adapters (SIM7020, SIM7000, Quectel BC95)
├── integrations/      # Protocol clients (MQTT, Blynk, HTTP)
├── utils/             # Logging, configuration, retry helpers
└── models/            # Command, response, and state data structures
```

Key abstractions:

- `BaseModule` — abstract base class defining the unified module interface.
- `ConnectionManager` — handles power, APN, attachment, and signal verification.
- `ATCommandInterface` — sends commands, manages retries and timeouts, parses responses.
- `CommandParser` — extracts structured data from raw AT responses.

Adding support for a new GSM module requires implementing a thin adapter class that inherits from `BaseModule`. The core, integrations, and utils packages remain untouched.

## Hardware Requirements

- **Microcontroller:** Raspberry Pi Pico (RP2040) running MicroPython v1.22 or later
- **GSM module:** SIMCom SIM7020E (NB-IoT). SIM7000 series and Quectel BC95 adapters planned in upcoming releases.
- **SIM card:** NB-IoT-provisioned SIM with valid APN
- **UART connection** between Pico and SIM7020E
- **Power control pin** (recommended) for module power management

## Installation

### Prerequisites

- [Python](https://www.python.org/) 3.12 or later
- [Poetry](https://python-poetry.org/) for dependency management
- A flashed Raspberry Pi Pico with MicroPython v1.22+

### Setup

Clone the repository:

```bash
git clone https://github.com/Violinist33/gsm_nbiot_lib.git
cd gsm_nbiot_lib
```

Install development dependencies:

```bash
poetry install
```

Create a `.env` file in the project root with your configuration:

```env
APN=nbiot
BLYNK_TOKEN=your_blynk_token_here
BROKER_ADDRESS=blynk.cloud
DEVICE_NAME=YourDeviceName
DEVICE_SECRET=your_device_secret_here
```

Upload the `sim7020py/` package and your main script to the Pico (using `ampy`, `mpremote`, or your preferred tool):

```bash
mpremote cp -r sim7020py/ :
mpremote cp config.py main.py :
```

## Quick Start

### Minimal Network Connection

```python
from machine import UART, Pin
from sim7020py import SIM7020, ATCommandError

uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1), timeout=5000)
sim = SIM7020(uart=uart, baudrate=115200, timeout=5)

try:
    sim.initialize()
    sim.set_apn("nbiot")
    sim.connect_network()
    rssi, ber = sim.get_signal_quality()
    print(f"Connected. RSSI={rssi}, BER={ber}")
except ATCommandError as e:
    print(f"Connection failed: {e}")
finally:
    sim.close()
```

### MQTT Publish

```python
sim.mqtt_new(broker_address="blynk.cloud", port=1883, keepalive=12000, buffer_size=1024)
sim.mqtt_connect(client_id="my_device", username="device", password=DEVICE_SECRET)
sim.mqtt_subscribe("downlink/ds/Integer V0")
sim.mqtt_publish("ds/LampStatus", "1")
```

### Blynk Integration

```python
from sim7020py import BlynkIntegration

blynk = BlynkIntegration(uart=uart, apn="nbiot", blynk_token=BLYNK_TOKEN, baudrate=115200, timeout=5)
blynk.connect()
blynk.send_value(virtual_pin=0, value="42")
value = blynk.get_value(virtual_pin=0)
blynk.disconnect()
```

A complete working example covering MQTT, Blynk, deep-sleep cycles, and lamp-state persistence is available in [`main.py`](./main.py).

## Configuration

All hardware and network parameters are centralized in [`config.py`](./config.py):

| Parameter | Description |
|---|---|
| `APN` | Access Point Name for the NB-IoT carrier |
| `BLYNK_TOKEN` | Authentication token for Blynk cloud |
| `BROKER_ADDRESS` | MQTT broker address |
| `DEVICE_NAME` / `DEVICE_SECRET` | MQTT client credentials |
| `LED_PIN`, `LED_PIN_MAIN` | GPIO pins for status indicators |
| `PWR_EN` | Power enable pin for the SIM7020E |
| `UART_PORT`, `UART_BAUDRATE` | UART configuration |

Sensitive values (tokens, secrets) should live in `.env`, not in `config.py`.

## Testing

The library uses Python's `unittest` framework with `unittest.mock` to simulate UART hardware, allowing tests to run without a physical device:

```bash
poetry run python -m unittest discover -s tests
```

Test coverage includes AT command transmission and parsing, network attachment logic, APN configuration, signal quality reporting, error propagation, Blynk integration, and resource cleanup.

## Documentation

- **API reference:** [https://jumbled-hose.surge.sh](https://jumbled-hose.surge.sh) (auto-generated with Sphinx)
- **Source:** docstrings in every module follow Google style
- **Local build:**

  ```bash
  cd docs && make html
  ```

## Roadmap

**Phase 1 (0–6 months): Hardware extensibility.** Module adapters for SIMCom SIM7000 and Quectel BC95/BC66 series, with conformance tests across all three families.

**Phase 2 (6–12 months): Protocol coverage.** Unified TCP/UDP sockets API, full HTTPS with certificate store, enhanced HTTP client (timeouts, redirects), and a power-consumption profile published as part of the documentation.

**Phase 3 (12+ months): Developer experience.** Adapter generator that scaffolds module stubs from AT manuals, hardware-in-the-loop test harness, and submission to the official `micropython-lib` ecosystem.

## Contributing

Contributions are welcome. Please open an [issue](https://github.com/Violinist33/gsm_nbiot_lib/issues) for bug reports or feature requests, and submit [pull requests](https://github.com/Violinist33/gsm_nbiot_lib/pulls) for improvements. For new module adapters, follow the pattern established in `sim7020py/sim7020.py` and provide accompanying unit tests.

## Citation

If you use this library in academic work, please cite the accompanying article:

```bibtex
@article{lupandin2025gsm,
  title   = {Model of an Open-Source MicroPython Library for GSM NB-IoT},
  author  = {Lupandin, Antonii and Kopieikin, Volodymyr and Khruslov, Maksym and Artyshchuk, Iryna and Shevchuk, Ruslan},
  journal = {Sensors},
  volume  = {25},
  number  = {17},
  pages   = {5322},
  year    = {2025},
  doi     = {10.3390/s25175322},
  url     = {https://doi.org/10.3390/s25175322},
  publisher = {MDPI}
}
```

## License

Distributed under the MIT License. See [LICENSE](./LICENSE) for details.

## Authors

- **Antonii Lupandin** — V. N. Karazin Kharkiv National University ([anlupandin@icloud.com](mailto:anlupandin@icloud.com))
- **Volodymyr Kopieikin** — V. N. Karazin Kharkiv National University
- **Maksym Khruslov** — V. N. Karazin Kharkiv National University
- **Iryna Artyshchuk** — University of the National Education Commission, Krakow
- **Ruslan Shevchuk** — University of Bielsko-Biala / West Ukrainian National University ([rshevchuk@ubb.edu.pl](mailto:rshevchuk@ubb.edu.pl))

## Acknowledgements

This work was conducted at the Department of Computer Systems and Robotics, Educational and Scientific Institute of Computer Science and Artificial Intelligence, V. N. Karazin Kharkiv National University.

---

© 2024–2025 Antonii Lupandin and contributors. Published under MIT License.
