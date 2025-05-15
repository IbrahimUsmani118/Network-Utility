#!/usr/bin/env python3
"""
Port Scanning Example - Demonstrates usage of nettools.port_tools module

This example script shows how to use the port scanning tools module to perform common
port-related network operations like checking individual ports, scanning port ranges,
finding common ports, and determining ports for specific services. All examples include
proper error handling.
"""

import sys
from rich.console import Console
from nettools.port_tools import scan_port, scan_ports, scan_common_ports, find_service_ports

# Initialize console for rich output
console = Console()

def demonstrate_single_port_scan():
    """Demonstrate scanning a single port with examples."""
    console.print("\n[bold green]Demonstrating Single Port Scanning[/bold green]")
    console.print("=" * 50)
    
    # Example 1: Scanning a typically open port
    try:
        console.print("\n[bold]Example 1: Scanning a typically open port[/bold]")
        target = "localhost"  # Use localhost for reliable testing
        port = 80  # HTTP port
        console.print(f"Scanning {target} on port {port} (HTTP)")
        port_num, is_open, service = scan_port(target, port)
        status = "[green]OPEN[/green]" if is_open else "[red]CLOSED[/red]"
        service_info = f" ({service})" if service else ""
        console.print(f"Port {port_num} is {status}{service_info}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")

    # Example 2: Scanning with a custom timeout
    try:
        console.print("\n[bold]Example 2: Scanning with a custom timeout[/bold]")
        target = "example.com"
        port = 443  # HTTPS port
        timeout = 2.0  # 2 seconds timeout
        console.print(f"Scanning {target} on port {port} (HTTPS) with a {timeout}s timeout")
        port_num, is_open, service = scan_port(target, port, timeout)
        status = "[green]OPEN[/green]" if is_open else "[red]CLOSED[/red]"
        service_info = f" ({service})" if service else ""
        console.print(f"Port {port_num} is {status}{service_info}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")

    # Example 3: Handling invalid port number
    try:
        console.print("\n[bold]Example 3: Handling invalid port number[/bold]")
        target = "localhost"
        port = 65536  # Invalid port (valid range is 0-65535)
        console.print(f"Attempting to scan {target} with invalid port {port}")
        result = scan_port(target, port)
        console.print("[yellow]Function handled invalid port appropriately.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")


def demonstrate_port_range_scanning():
    """Demonstrate scanning a range of ports with examples."""
    console.print("\n[bold green]Demonstrating Port Range Scanning[/bold green]")
    console.print("=" * 50)
    
    # Example 1: Scanning specific ports
    try:
        console.print("\n[bold]Example 1: Scanning specific ports[/bold]")
        target = "localhost"
        port_list = [22, 80, 443]  # SSH, HTTP, HTTPS
        console.print(f"Scanning {target} on ports: {', '.join(str(p) for p in port_list)}")
        
        # Use non-verbose mode to avoid cluttering the output
        results = scan_ports(target, port_list, verbose=False)
        
        # Display results manually for the example
        console.print(f"Scan completed, found {len(results)} open port(s):")
        for port, is_open, service in results:
            console.print(f"  Port {port}: [green]OPEN[/green] ({service})")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")

    # Example 2: Scanning a port range
    try:
        console.print("\n[bold]Example 2: Scanning a port range[/bold]")
        target = "localhost"
        # Scan a small range for demonstration (would be larger in real usage)
        port_range = (79, 81)
        console.print(f"Scanning {target} on port range: {port_range[0]}-{port_range[1]}")
        
        # Use shorter timeout for faster scanning in example
        results = scan_ports(target, port_range, timeout=0.5, verbose=False)
        
        # Display results manually for the example
        console.print(f"Scan completed, found {len(results)} open port(s):")
        for port, is_open, service in results:
            console.print(f"  Port {port}: [green]OPEN[/green] ({service})")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
    
    # Example 3: Handling unreachable host
    try:
        console.print("\n[bold]Example 3: Handling unreachable host[/bold]")
        target = "nonexistent-host-123.local"  # Non-existent hostname
        port_range = [80]  # Just check one port to save time
        console.print(f"Attempting to scan unreachable host: {target}")
        
        # Use shorter timeout and non-verbose mode
        results = scan_ports(target, port_range, timeout=0.5, verbose=False)
        
        if not results:
            console.print("[yellow]As expected, the scan handled the unreachable host gracefully.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")


def demonstrate_common_ports_scanning():
    """Demonstrate scanning common ports functionality."""
    console.print("\n[bold green]Demonstrating Common Ports Scanning[/bold green]")
    console.print("=" * 50)
    
    # Example: Scanning common ports on localhost
    try:
        console.print("\n[bold]Example: Scanning common ports[/bold]")
        target = "localhost"
        console.print(f"Scanning common ports on {target}")
        console.print("[yellow]Note: This will scan about 20 commonly used ports[/yellow]")
        
        # Use non-verbose mode to avoid cluttering example output
        # and set shorter timeout for demonstration
        results = scan_common_ports(target, timeout=0.2, verbose=False)
        
        # Display results manually for the example
        console.print(f"Scan completed, found {len(results)} open common port(s):")
        if results:
            for port, is_open, service in results:
                console.print(f"  Port {port}: [green]OPEN[/green] ({service})")
        else:
            console.print("  [yellow]No common ports open on localhost[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")


def demonstrate_service_port_lookup():
    """Demonstrate looking up ports for a specific service."""
    console.print("\n[bold green]Demonstrating Service Port Lookup[/bold green]")
    console.print("=" * 50)
    
    # Example 1: Finding ports for a common service
    try:
        console.print("\n[bold]Example 1: Finding ports for a common service[/bold]")
        service = "http"
        console.print(f"Looking up ports for '{service}' service")
        ports = find_service_ports(service)
        if ports:
            console.print(f"Found {len(ports)} port(s) for {service}: {', '.join(str(p) for p in ports)}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")

    # Example 2: Finding ports for another common service
    try:
        console.print("\n[bold]Example 2: Finding ports for another service[/bold]")
        service = "ssh"
        console.print(f"Looking up ports for '{service}' service")
        ports = find_service_ports(service)
        if ports:
            console.print(f"Found {len(ports)} port(s) for {service}: {', '.join(str(p) for p in ports)}")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
    
    # Example 3: Handling non-existent service
    try:
        console.print("\n[bold]Example 3: Handling non-existent service[/bold]")
        service = "nonexistentservice123"
        console.print(f"Looking up ports for non-existent service: '{service}'")
        ports = find_service_ports(service)
        if not ports:
            console.print("[yellow]As expected, no ports were found for the non-existent service.[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")


def main():
    """Main function to run all demonstrations."""
    console.print("[bold magenta]NetTools Port Scanning Utilities Example[/bold magenta]")
    console.print("This script demonstrates the usage of port scanning tools from the nettools package.")
    console.print("[yellow]Note: Some examples may take a few seconds to complete due to network operations.[/yellow]")
    
    # Run demonstrations
    demonstrate_single_port_scan()
    demonstrate_port_range_scanning()
    demonstrate_common_ports_scanning()
    demonstrate_service_port_lookup()
    
    console.print("\n[bold green]All port scanning demonstrations completed![/bold green]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Example script interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Fatal error:[/bold red] {str(e)}")
        sys.exit(1)