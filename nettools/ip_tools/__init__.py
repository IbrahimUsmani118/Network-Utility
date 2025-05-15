"""
IP Tools - Module for IP address handling and subnet analysis.

This module provides utilities for working with IP addresses, including
resolving hostnames to IP addresses, analyzing subnets, and performing
ICMP ping operations. It simplifies common IP-related networking tasks.
"""

# Import key functions from ip_utils for easier access
from .ip_utils import resolve_ip, analyze_subnet, ping