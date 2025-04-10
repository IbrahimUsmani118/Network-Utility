"""
Port Tools - Module for port scanning and service discovery utilities.

This module provides utilities for port operations, including scanning for open ports,
identifying running services, and checking connectivity on specific ports.
It offers simple functions to perform common port-related networking tasks.
"""

# Import key functions from port_scanner for easier access
from .port_scanner import scan_port, scan_ports