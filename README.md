# NetTools

A comprehensive Python networking utility toolkit that simplifies common networking tasks. NetTools provides a collection of utilities for IP address operations, DNS lookups, port scanning, and web data extraction.

## Features

- **IP Tools**: Resolve hostnames to IP addresses, analyze subnets, and perform ICMP ping operations
- **DNS Tools**: Perform DNS lookups for various record types (A, AAAA, MX, CNAME, TXT, etc.) and reverse DNS lookups
- **Port Tools**: Scan individual ports or port ranges, check common ports, and find service-specific ports
- **Web Tools**: Extract data from web pages and measure network connection speeds

## Installation

### Requirements

- Python 3.7 or higher
- Required packages: rich, requests, dnspython

### From PyPI (recommended)

```bash
pip install nettools
```

### From Source

1. Clone the repository:
```bash
git clone https://github.com/nettools/nettools.git
cd nettools
```

2. Install in development mode:
```bash
pip install -e .
```

## Usage

NetTools can be used both as a command-line tool and as a Python library.

### Command Line Interface

NetTools provides an interactive CLI with a menu-driven interface:

```bash
nettools
```

Or use direct commands:

```bash
# IP address resolution
nettools ip resolve example.com

# Subnet analysis
nettools ip subnet 192.168.1.0 24

# Ping a host
nettools ip ping google.com -c 5

# DNS lookup
nettools dns lookup example.com -t MX

# Reverse DNS lookup
nettools dns reverse 8.8.8.8

# Port scanning
nettools port scan example.com 80-100
nettools port common localhost

# Web data extraction
nettools web extract https://example.com

# Speed test
nettools web speed
```

### Python Library

```python
# Import specific modules
from nettools.ip_tools import resolve_ip, analyze_subnet, ping
from nettools.dns_tools import dns_lookup, reverse_dns_lookup
from nettools.port_tools import scan_port, scan_ports, scan_common_ports
from nettools.web_tools import extract_web_data, speed_test

# Resolve IP address
ip = resolve_ip('example.com')
print(f"IP address: {ip}")

# Analyze subnet
subnet_info = analyze_subnet('192.168.1.0', '24')
print(f"Network address: {subnet_info['network_address']}")
print(f"Broadcast address: {subnet_info['broadcast_address']}")

# Scan ports
open_ports = scan_ports('example.com', (80, 100))
for port, is_open, service in open_ports:
    print(f"Port {port} is open: {service}")
```

## Module Examples

### IP Tools

```python
from nettools.ip_tools import resolve_ip, analyze_subnet, ping

# Resolve hostname to IP
ip = resolve_ip('google.com')

# Analyze subnet
subnet = analyze_subnet('10.0.0.0', '8')

# Ping a host
ping_results = ping('8.8.8.8', count=5)
```

### DNS Tools

```python
from nettools.dns_tools import dns_lookup, reverse_dns_lookup

# Look up DNS records
mx_records = dns_lookup('gmail.com', record_type='MX')

# Reverse DNS lookup
hostname = reverse_dns_lookup('8.8.8.8')
```

### Port Tools

```python
from nettools.port_tools import scan_port, scan_ports, scan_common_ports

# Check if specific port is open
port, is_open, service = scan_port('example.com', 80)

# Scan a range of ports
open_ports = scan_ports('example.com', (1, 100))

# Scan common ports
open_common_ports = scan_common_ports('example.com')
```

### Web Tools

```python
from nettools.web_tools import extract_web_data, speed_test

# Extract data from a web page
web_content = extract_web_data('https://example.com')

# Test network speed
speed_results = speed_test()
print(f"Download: {speed_results['download_speed']} Mbps")
print(f"Upload: {speed_results['upload_speed']} Mbps")
```

## Development

### Setting Up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/nettools/nettools.git
cd nettools
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Install all dependencies:
```bash
pip install -r requirements.txt
```

### Running Tests

Run tests with pytest:

```bash
pytest tests/
```

For test coverage report:

```bash
pytest --cov=nettools tests/
```

### Code Style

NetTools uses flake8 for code linting and black for code formatting:

```bash
# Check code style
flake8 nettools tests

# Format code
black nettools tests
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request