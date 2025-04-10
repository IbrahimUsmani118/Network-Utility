"""
Command Line Interface for NetTools.

This module provides a comprehensive command-line interface for all networking tools
in the NetTools package. It integrates IP tools, DNS tools, port scanning, and web utilities
into a unified interface with both interactive menu mode and direct command-line arguments.
"""

import sys
import argparse
import textwrap
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

# Import utility functions from submodules
from nettools.ip_tools.ip_utils import resolve_ip, analyze_subnet, ping
from nettools.dns_tools.dns_utils import dns_lookup, reverse_dns_lookup, bulk_dns_lookup
from nettools.port_tools.port_scanner import scan_port, scan_ports, scan_common_ports, find_service_ports
from nettools.web_tools.web_utils import extract_web_data, speed_test

# Create console for rich text output
console = Console()

def print_banner():
    """Print the application banner."""
    banner_text = """
    █▄░█ █▀▀ ▀█▀ ▀█▀ █▀█ █▀█ █░░ █▀
    █░▀█ ██▄ ░█░ ░█░ █▄█ █▄█ █▄▄ ▄█
    """
    console.print(Panel(banner_text, subtitle="Network Utilities Toolkit v0.1.0", 
                        style="bold green"))

def ip_tools_menu():
    """Display and handle the IP tools menu."""
    console.print("\n[bold cyan]IP Tools Menu[/bold cyan]")
    console.print("1. Resolve IP address")
    console.print("2. Analyze subnet")
    console.print("3. Ping host")
    console.print("0. Back to main menu")
    
    choice = Prompt.ask("Enter your choice", choices=["0", "1", "2", "3"], default="0")
    
    if choice == "1":
        resolve_ip()
    elif choice == "2":
        analyze_subnet()
    elif choice == "3":
        ping()
    
    return choice != "0"  # Return True to stay in this menu, False to go back

def dns_tools_menu():
    """Display and handle the DNS tools menu."""
    console.print("\n[bold cyan]DNS Tools Menu[/bold cyan]")
    console.print("1. DNS lookup (A record)")
    console.print("2. DNS lookup (custom record type)")
    console.print("3. Reverse DNS lookup")
    console.print("0. Back to main menu")
    
    choice = Prompt.ask("Enter your choice", choices=["0", "1", "2", "3"], default="0")
    
    if choice == "1":
        dns_lookup()
    elif choice == "2":
        domain = input("Enter domain name: ")
        record_type = input("Enter record type (A, AAAA, MX, CNAME, TXT, NS, SOA): ")
        dns_lookup(domain, record_type)
    elif choice == "3":
        reverse_dns_lookup()
    
    return choice != "0"  # Return True to stay in this menu, False to go back

def port_tools_menu():
    """Display and handle the port scanning tools menu."""
    console.print("\n[bold cyan]Port Scanning Tools Menu[/bold cyan]")
    console.print("1. Scan specific port")
    console.print("2. Scan port range")
    console.print("3. Scan common ports")
    console.print("4. Find ports for a service")
    console.print("0. Back to main menu")
    
    choice = Prompt.ask("Enter your choice", choices=["0", "1", "2", "3", "4"], default="0")
    
    if choice == "1":
        target = input("Enter target hostname or IP: ")
        port = int(input("Enter port number: "))
        result = scan_port(target, port)
        if result[1]:  # If port is open
            console.print(f"[green]Port {port} is open[/green] ({result[2]})")
        else:
            console.print(f"[red]Port {port} is closed[/red]")
    elif choice == "2":
        scan_ports()
    elif choice == "3":
        scan_common_ports()
    elif choice == "4":
        service = input("Enter service name (e.g., http, ssh, ftp): ")
        find_service_ports(service)
    
    return choice != "0"  # Return True to stay in this menu, False to go back

def web_tools_menu():
    """Display and handle the web tools menu."""
    console.print("\n[bold cyan]Web Tools Menu[/bold cyan]")
    console.print("1. Extract web page data")
    console.print("2. Internet speed test")
    console.print("0. Back to main menu")
    
    choice = Prompt.ask("Enter your choice", choices=["0", "1", "2"], default="0")
    
    if choice == "1":
        extract_web_data()
    elif choice == "2":
        speed_test()
    
    return choice != "0"  # Return True to stay in this menu, False to go back

def interactive_menu():
    """Display and handle the main interactive menu."""
    print_banner()
    
    while True:
        console.print("\n[bold green]Main Menu[/bold green]")
        console.print("1. IP Tools")
        console.print("2. DNS Tools")
        console.print("3. Port Scanning Tools")
        console.print("4. Web Tools")
        console.print("0. Exit")
        
        choice = Prompt.ask("Enter your choice", choices=["0", "1", "2", "3", "4"], default="0")
        
        if choice == "1":
            while ip_tools_menu():
                pass
        elif choice == "2":
            while dns_tools_menu():
                pass
        elif choice == "3":
            while port_tools_menu():
                pass
        elif choice == "4":
            while web_tools_menu():
                pass
        elif choice == "0":
            console.print("[yellow]Exiting program...[/yellow]")
            return

def setup_argparse():
    """Set up command-line argument parsing."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
        NetTools - A comprehensive network utilities toolkit
        
        This tool provides various networking utilities including IP address handling,
        DNS resolution, port scanning, and web data extraction.
        """)
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # IP tools
    ip_parser = subparsers.add_parser("ip", help="IP address utilities")
    ip_subparsers = ip_parser.add_subparsers(dest="ip_command", help="IP command to run")
    
    # Resolve IP
    resolve_parser = ip_subparsers.add_parser("resolve", help="Resolve hostname to IP address")
    resolve_parser.add_argument("hostname", help="Hostname to resolve", nargs="?")
    
    # Subnet analysis
    subnet_parser = ip_subparsers.add_parser("subnet", help="Analyze subnet")
    subnet_parser.add_argument("address", help="IP address", nargs="?")
    subnet_parser.add_argument("mask", help="Subnet mask in CIDR notation", nargs="?")
    
    # Ping
    ping_parser = ip_subparsers.add_parser("ping", help="Ping a host")
    ping_parser.add_argument("target", help="Target to ping", nargs="?")
    ping_parser.add_argument("-c", "--count", type=int, default=4, help="Number of packets to send")
    
    # DNS tools
    dns_parser = subparsers.add_parser("dns", help="DNS utilities")
    dns_subparsers = dns_parser.add_subparsers(dest="dns_command", help="DNS command to run")
    
    # DNS lookup
    lookup_parser = dns_subparsers.add_parser("lookup", help="Lookup DNS records")
    lookup_parser.add_argument("domain", help="Domain to lookup", nargs="?")
    lookup_parser.add_argument("-t", "--type", default="A", help="Record type (A, AAAA, MX, etc.)")
    
    # Reverse DNS lookup
    reverse_parser = dns_subparsers.add_parser("reverse", help="Reverse DNS lookup")
    reverse_parser.add_argument("ip", help="IP address to lookup", nargs="?")
    
    # Port tools
    port_parser = subparsers.add_parser("port", help="Port scanning utilities")
    port_subparsers = port_parser.add_subparsers(dest="port_command", help="Port command to run")
    
    # Scan port
    scan_port_parser = port_subparsers.add_parser("scan", help="Scan ports")
    scan_port_parser.add_argument("target", help="Target to scan", nargs="?")
    scan_port_parser.add_argument("ports", help="Port or port range (e.g. 80 or 1-1024 or 22,80,443)", nargs="?")
    scan_port_parser.add_argument("-t", "--timeout", type=float, default=1, help="Timeout in seconds")
    
    # Scan common ports
    common_parser = port_subparsers.add_parser("common", help="Scan common ports")
    common_parser.add_argument("target", help="Target to scan", nargs="?")
    
    # Find service ports
    service_parser = port_subparsers.add_parser("service", help="Find ports for a service")
    service_parser.add_argument("service", help="Service name (e.g. http, ssh)", nargs="?")
    
    # Web tools
    web_parser = subparsers.add_parser("web", help="Web utilities")
    web_subparsers = web_parser.add_subparsers(dest="web_command", help="Web command to run")
    
    # Extract web data
    extract_parser = web_subparsers.add_parser("extract", help="Extract web page data")
    extract_parser.add_argument("url", help="URL to extract data from", nargs="?")
    
    # Speed test
    speed_parser = web_subparsers.add_parser("speed", help="Internet speed test")
    
    return parser

def parse_port_range(port_str):
    """Parse port range string into a list or tuple of ports."""
    if "-" in port_str:
        start, end = map(int, port_str.split("-"))
        return (start, end)
    elif "," in port_str:
        return list(map(int, port_str.split(",")))
    else:
        return [int(port_str)]

def process_args(args):
    """Process command-line arguments."""
    if args.command == "ip":
        if args.ip_command == "resolve":
            resolve_ip(args.hostname)
        elif args.ip_command == "subnet":
            analyze_subnet(args.address, args.mask)
        elif args.ip_command == "ping":
            ping(args.target, args.count)
        else:
            ip_tools_menu()
            
    elif args.command == "dns":
        if args.dns_command == "lookup":
            dns_lookup(args.domain, args.type)
        elif args.dns_command == "reverse":
            reverse_dns_lookup(args.ip)
        else:
            dns_tools_menu()
            
    elif args.command == "port":
        if args.port_command == "scan":
            if args.ports:
                port_range = parse_port_range(args.ports)
                scan_ports(args.target, port_range, args.timeout)
            else:
                scan_ports(args.target)
        elif args.port_command == "common":
            scan_common_ports(args.target)
        elif args.port_command == "service":
            find_service_ports(args.service)
        else:
            port_tools_menu()
            
    elif args.command == "web":
        if args.web_command == "extract":
            extract_web_data(args.url)
        elif args.web_command == "speed":
            speed_test()
        else:
            web_tools_menu()
    else:
        interactive_menu()

def main():
    """Main entry point for the CLI."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if len(sys.argv) > 1:
        # Command-line arguments were provided
        process_args(args)
    else:
        # No arguments, start interactive mode
        interactive_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Program interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)