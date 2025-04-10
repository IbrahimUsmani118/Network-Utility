"""
NetTools - A comprehensive Python networking utility package.

This package provides tools for various networking operations including IP address handling,
DNS resolution, port scanning, and web data extraction. It aims to simplify common
networking tasks for both beginners and advanced users.
"""

__version__ = '0.1.0'

# Import submodules for easier access
from . import ip_tools
from . import dns_tools
from . import port_tools
from . import web_tools

# For convenience, expose key functions at package level
from .ip_tools.ip_utils import resolve_ip, analyze_subnet
from .web_tools.web_utils import extract_web_data
from .dns_tools.dns_utils import dns_lookup, reverse_dns_lookup
from .port_tools.port_scanner import scan_port, scan_ports