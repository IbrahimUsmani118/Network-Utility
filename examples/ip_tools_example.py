#!/usr/bin/env python3
"""
IP Tools Example - Demonstrates usage of nettools.ip_tools module

This example script shows how to use the IP tools module to perform common
network operations like resolving hostnames to IP addresses, analyzing subnet
information, and pinging hosts with proper error handling.
"""

import sys
from rich.console import Console
from nettools.ip_tools import resolve_ip, analyze_subnet, ping

# Initialize console for rich output
console = Console()

def demonstrate_ip_resolution():
    """Demonstrate hostname to IP address resolution with examples."""
    console.print("\n[bold green]Demonstrating IP Address Resolution[/bold green]")
    console.print("=" * 50)
    
    # Example 1: Resolving a valid hostname
    try:
        console.print("\n[bold]Example 1: Resolving a valid hostname[/bold]")
        hostname = "www.google.com"
        console.print(f"Resolving hostname: {hostname}")
        ip = resolve_ip(hostname)
        if ip:
            console.print(f"[green]Success![/green] Resolved {hostname} to {ip}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")

    # Example 2: Handling invalid hostname
    try:
        console.print("\n[bold]Example 2: Handling an invalid hostname[/bold]")
        hostname = "invalid-hostname-that-does-not-exist.xyz"
        console.print(f"Attempting to resolve invalid hostname: {hostname}")
        ip = resolve_ip(hostname)
        if ip is None:
            console.print("[yellow]As expected, the invalid hostname couldn't be resolved.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")

    # Example 3: Resolving IP of local machine
    try:
        console.print("\n[bold]Example 3: Resolving localhost[/bold]")
        hostname = "localhost"
        console.print(f"Resolving hostname: {hostname}")
        ip = resolve_ip(hostname)
        if ip:
            console.print(f"[green]Success![/green] Resolved {hostname} to {ip}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")


def demonstrate_subnet_analysis():
    """Demonstrate subnet analysis with examples."""
    console.print("\n[bold green]Demonstrating Subnet Analysis[/bold green]")
    console.print("=" * 50)
    
    # Example 1: Analyzing a simple Class C network
    try:
        console.print("\n[bold]Example 1: Analyzing a Class C network[/bold]")
        ip = "192.168.1.0"
        mask = "24"
        console.print(f"Analyzing subnet: {ip}/{mask}")
        result = analyze_subnet(ip, mask)
        if result:
            console.print("[green]Subnet analysis completed successfully![/green]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
    
    # Example 2: Analyzing a small subnet
    try:
        console.print("\n[bold]Example 2: Analyzing a small subnet[/bold]")
        ip = "10.0.0.0"
        mask = "30"
        console.print(f"Analyzing subnet: {ip}/{mask}")
        result = analyze_subnet(ip, mask)
        if result:
            console.print("[green]Small subnet analysis completed successfully![/green]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
    
    # Example 3: Handling invalid input
    try:
        console.print("\n[bold]Example 3: Handling invalid subnet input[/bold]")
        ip = "192.168.1"  # Invalid IP (missing octet)
        mask = "24"
        console.print(f"Attempting to analyze invalid subnet: {ip}/{mask}")
        result = analyze_subnet(ip, mask)
        if result is None:
            console.print("[yellow]As expected, the invalid subnet couldn't be analyzed.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")


def demonstrate_ping():
    """Demonstrate ping functionality with examples."""
    console.print("\n[bold green]Demonstrating Ping Functionality[/bold green]")
    console.print("=" * 50)
    
    # Example 1: Ping a valid host
    try:
        console.print("\n[bold]Example 1: Pinging a valid host[/bold]")
        target = "8.8.8.8"  # Google's DNS
        count = 3
        console.print(f"Pinging {target} with {count} packets")
        result = ping(target, count)
        if result:
            console.print(f"[green]Ping completed successfully![/green]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
    
    # Example 2: Ping with custom count
    try:
        console.print("\n[bold]Example 2: Pinging with custom packet count[/bold]")
        target = "1.1.1.1"  # Cloudflare's DNS
        count = 2
        console.print(f"Pinging {target} with {count} packets")
        result = ping(target, count)
        if result:
            console.print(f"[green]Ping with custom count completed successfully![/green]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
    
    # Example 3: Handling unreachable host
    # This might take some time to timeout
    try:
        console.print("\n[bold]Example 3: Handling unreachable host[/bold]")
        target = "192.168.123.254"  # Likely unreachable address
        count = 1  # Use just 1 packet to make it faster
        console.print(f"Attempting to ping unreachable host: {target}")
        console.print("[yellow]Note: This may take a few seconds to timeout...[/yellow]")
        result = ping(target, count)
        if result is None:
            console.print("[yellow]As expected, the host is unreachable.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")


def main():
    """Main function to run all demonstrations."""
    console.print("[bold magenta]NetTools IP Utilities Example[/bold magenta]")
    console.print("This script demonstrates the usage of IP tools from the nettools package.")
    
    # Run demonstrations
    demonstrate_ip_resolution()
    demonstrate_subnet_analysis()
    demonstrate_ping()
    
    console.print("\n[bold green]All demonstrations completed![/bold green]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Example script interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Fatal error:[/bold red] {str(e)}")
        sys.exit(1)