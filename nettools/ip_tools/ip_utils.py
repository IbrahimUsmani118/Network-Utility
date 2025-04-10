"""
IP address utilities for network operations.

This module provides functions for working with IP addresses, including DNS resolution,
subnet analysis, and ping operations. It offers a simple interface for common
IP-related networking tasks with proper error handling.
"""

import socket
import ipaddress
import subprocess
import re
import platform
import time
from rich.console import Console

console = Console()


def resolve_ip(hostname=None):
    """
    Resolve a hostname to its corresponding IP address.
    
    Args:
        hostname (str, optional): The hostname to resolve. If None, prompts the user for input.
        
    Returns:
        str: The IP address corresponding to the hostname.
        
    Raises:
        socket.gaierror: If the hostname cannot be resolved.
    """
    try:
        if hostname is None:
            hostname = input("Enter a URL to read its IP address: ")
        
        ip_address = socket.gethostbyname(hostname)
        console.print(f"IP address for {hostname}: {ip_address}")
        return ip_address
    except socket.gaierror:
        console.print(f"[bold red]Error:[/bold red] Could not resolve IP address for {hostname}")
        return None


def analyze_subnet(ip_address=None, mask=None):
    """
    Analyze a subnet based on an IP address and subnet mask.
    
    Args:
        ip_address (str, optional): The IP address to analyze. If None, prompts the user for input.
        mask (str, optional): The subnet mask in CIDR notation (e.g., '24'). If None, prompts the user for input.
        
    Returns:
        dict: A dictionary containing network information (network_address, broadcast_address, num_addresses).
        
    Raises:
        ValueError: If the IP address or subnet mask is invalid.
    """
    try:
        if ip_address is None:
            ip_address = input("Enter an IP address to subnet (e.g. 192.168.0.0): ")
        if mask is None:
            mask = input("Enter the subnet mask (e.g. 24): ")
        
        network = ipaddress.ip_network(f"{ip_address}/{mask}", strict=False)
        result = {
            'network_address': str(network.network_address),
            'broadcast_address': str(network.broadcast_address),
            'num_addresses': network.num_addresses,
            'netmask': str(network.netmask),
            'hosts': [str(ip) for ip in network.hosts()][:5]  # Limiting to 5 hosts to avoid excessive output
        }
        
        console.print(f"Network address: {result['network_address']}")
        console.print(f"Broadcast address: {result['broadcast_address']}")
        console.print(f"Number of addresses: {result['num_addresses']}")
        console.print(f"Netmask: {result['netmask']}")
        if len(result['hosts']) > 0:
            console.print(f"First few host addresses: {', '.join(result['hosts'])}" +  
                         (f" (showing 5 of {network.num_addresses-2})" if network.num_addresses > 7 else ""))
        
        return result
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] Invalid IP address or mask - {str(e)}")
        return None


def ping(target=None, count=4):
    """
    Ping a target IP or hostname and report statistics.
    
    Args:
        target (str, optional): The IP address or hostname to ping. If None, prompts the user for input.
        count (int, optional): Number of ping packets to send. Defaults to 4.
        
    Returns:
        dict: A dictionary containing ping statistics (packets_sent, packets_received, loss_percentage, min_time, max_time, avg_time).
        
    Raises:
        subprocess.SubprocessError: If the ping command fails.
    """
    if target is None:
        target = input("Enter an IP address or hostname to ping: ")
    
    try:
        # Determine the ping command based on the operating system
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, str(count), target]
        
        console.print(f"Pinging {target} with {count} packets...")
        
        # Execute ping command
        start_time = time.time()
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()
        end_time = time.time()
        
        if process.returncode != 0:
            console.print(f"[bold red]Error:[/bold red] Failed to ping {target}")
            return None
        
        # Parse the results
        output_str = output.decode('utf-8')
        
        # Initialize statistics
        stats = {
            'packets_sent': count,
            'packets_received': 0,
            'loss_percentage': 100.0,
            'min_time': None,
            'max_time': None,
            'avg_time': None,
            'total_time': round(end_time - start_time, 2)
        }
        
        # Extract packet statistics based on OS
        if platform.system().lower() == "windows":
            # Windows ping output parsing
            received_match = re.search(r'Received = (\d+)', output_str)
            if received_match:
                stats['packets_received'] = int(received_match.group(1))
                
            loss_match = re.search(r'Lost = (\d+) \((\d+)%', output_str)
            if loss_match:
                stats['loss_percentage'] = int(loss_match.group(2))
                
            times_match = re.search(r'Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms', output_str)
            if times_match:
                stats['min_time'] = int(times_match.group(1))
                stats['max_time'] = int(times_match.group(2))
                stats['avg_time'] = int(times_match.group(3))
        else:
            # Unix-like ping output parsing
            received_match = re.search(r'(\d+) packets transmitted, (\d+) received', output_str)
            if received_match:
                stats['packets_received'] = int(received_match.group(2))
                
            loss_match = re.search(r'(\d+)% packet loss', output_str)
            if loss_match:
                stats['loss_percentage'] = int(loss_match.group(1))
                
            times_match = re.search(r'min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)', output_str)
            if times_match:
                stats['min_time'] = float(times_match.group(1))
                stats['avg_time'] = float(times_match.group(2))
                stats['max_time'] = float(times_match.group(3))
        
        # Print results
        console.print(f"[green]Ping results for {target}:[/green]")
        console.print(f"Packets: {stats['packets_received']} received / {stats['packets_sent']} sent ({stats['loss_percentage']}% loss)")
        
        if stats['min_time'] is not None:
            console.print(f"Round-trip times: min={stats['min_time']}ms, avg={stats['avg_time']}ms, max={stats['max_time']}ms")
        console.print(f"Total time: {stats['total_time']}s")
        
        return stats
        
    except (subprocess.SubprocessError, Exception) as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return None