"""
Port scanning utilities for network operations.

This module provides functions for scanning network ports, including checking individual ports
and scanning port ranges. It implements multi-threading for efficient scanning and proper
error handling for network operations.
"""

import socket
import time
import threading
import concurrent.futures
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

console = Console()

def scan_port(target, port, timeout=1):
    """
    Check if a specific port is open on the target host.
    
    Args:
        target (str): The target hostname or IP address to scan.
        port (int): The port number to check.
        timeout (float, optional): The timeout for the connection attempt in seconds. Defaults to 1.
        
    Returns:
        tuple: A tuple containing (port_number, is_open, service_name).
        
    Raises:
        socket.error: If there's an error creating the socket.
        ValueError: If the port number is invalid.
    """
    try:
        # Validate port number
        if not 0 <= port <= 65535:
            raise ValueError(f"Invalid port number: {port}. Port must be between 0 and 65535.")
            
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Attempt to connect
        result = sock.connect_ex((target, port))
        is_open = (result == 0)
        
        # Get service name if port is open
        service_name = ""
        if is_open:
            try:
                service_name = socket.getservbyport(port)
            except (socket.error, OSError):
                service_name = "unknown"
        
        sock.close()
        return (port, is_open, service_name)
        
    except socket.gaierror:
        console.print(f"[bold red]Error:[/bold red] Hostname {target} could not be resolved")
        return (port, False, "")
    except socket.error as e:
        console.print(f"[bold red]Error:[/bold red] Could not connect to {target}:{port} - {str(e)}")
        return (port, False, "")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return (port, False, "")
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        return (port, False, "")

def _scan_worker(args):
    """
    Worker function for multi-threaded port scanning.
    
    Args:
        args (tuple): A tuple containing (target, port, timeout).
        
    Returns:
        tuple: Result of scan_port function.
    """
    target, port, timeout = args
    return scan_port(target, port, timeout)

def scan_ports(target=None, port_range=None, timeout=1, max_workers=100, verbose=True):
    """
    Scan a range of ports on the target host.
    
    Args:
        target (str, optional): The target hostname or IP address to scan. If None, prompts the user for input.
        port_range (tuple or list, optional): The range of ports to scan (start, end) inclusive. 
                                             If None, prompts the user for input.
        timeout (float, optional): The timeout for each connection attempt in seconds. Defaults to 1.
        max_workers (int, optional): Maximum number of concurrent threads. Defaults to 100.
        verbose (bool, optional): Whether to print progress and results. Defaults to True.
        
    Returns:
        list: A list of tuples (port, is_open, service_name) for open ports.
        
    Raises:
        ValueError: If the port range is invalid.
    """
    try:
        # Get target if not provided
        if target is None:
            target = input("Enter target hostname or IP address to scan: ")
        
        # Get port range if not provided
        if port_range is None:
            port_range_input = input("Enter port range to scan (e.g. 1-1024 or 22,80,443): ")
            
            # Parse port range input
            if "-" in port_range_input:
                start, end = map(int, port_range_input.split("-"))
                port_range = (start, end)
            elif "," in port_range_input:
                ports = list(map(int, port_range_input.split(",")))
                port_range = ports
            else:
                try:
                    port = int(port_range_input)
                    port_range = [port]
                except ValueError:
                    raise ValueError("Invalid port range format. Use '1-1024' for a range or '22,80,443' for specific ports.")
        
        # Create list of ports to scan
        ports_to_scan = []
        if isinstance(port_range, tuple) and len(port_range) == 2:
            start, end = port_range
            if start > end:
                start, end = end, start
            ports_to_scan = list(range(start, end + 1))
        elif isinstance(port_range, list):
            ports_to_scan = port_range
        else:
            raise ValueError("Invalid port range format")
        
        # Validate port numbers
        for port in ports_to_scan:
            if not 0 <= port <= 65535:
                raise ValueError(f"Invalid port number: {port}. Port must be between 0 and 65535.")
        
        if verbose:
            console.print(f"[bold]Scanning {len(ports_to_scan)} ports on {target}...[/bold]")
            start_time = time.time()
        
        # Prepare scan parameters
        scan_params = [(target, port, timeout) for port in ports_to_scan]
        
        # Create result storage
        results = []
        open_ports = []
        
        # Use thread pool for concurrent scanning
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            if verbose:
                # Show progress bar when verbose
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                ) as progress:
                    task = progress.add_task("[cyan]Scanning ports...", total=len(ports_to_scan))
                    
                    # Process results as they come in
                    for i, result in enumerate(executor.map(_scan_worker, scan_params)):
                        progress.update(task, completed=i+1)
                        results.append(result)
                        if result[1]:  # If port is open
                            open_ports.append(result)
            else:
                # No progress bar in non-verbose mode
                results = list(executor.map(_scan_worker, scan_params))
                open_ports = [result for result in results if result[1]]
        
        # Print results
        if verbose:
            scan_time = time.time() - start_time
            
            # Create a table for results
            table = Table(title=f"Scan Results for {target}")
            table.add_column("Port", justify="right", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Service", style="magenta")
            
            for port, is_open, service_name in open_ports:
                table.add_row(str(port), "OPEN", service_name)
                
            console.print(table)
            console.print(f"Scan completed in {scan_time:.2f} seconds")
            console.print(f"Found {len(open_ports)} open ports out of {len(ports_to_scan)} scanned")
        
        return open_ports
        
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return []
    except KeyboardInterrupt:
        console.print("[bold yellow]Scan interrupted by user[/bold yellow]")
        return []
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {str(e)}")
        return []

def scan_common_ports(target=None, timeout=1, verbose=True):
    """
    Scan common ports on the target host.
    
    Args:
        target (str, optional): The target hostname or IP address to scan. If None, prompts the user for input.
        timeout (float, optional): The timeout for each connection attempt in seconds. Defaults to 1.
        verbose (bool, optional): Whether to print progress and results. Defaults to True.
        
    Returns:
        list: A list of tuples (port, is_open, service_name) for open ports.
    """
    # List of common ports to scan
    common_ports = [
        21, 22, 23, 25, 53, 80, 110, 115, 135, 139,
        143, 194, 443, 445, 1433, 3306, 3389, 5632, 5900, 8080
    ]
    
    if verbose:
        console.print("[bold]Scanning common ports...[/bold]")
    
    return scan_ports(target, common_ports, timeout, verbose=verbose)

def find_service_ports(service_name, verbose=True):
    """
    Find ports associated with a specific service name.
    
    Args:
        service_name (str): The service name to look up.
        verbose (bool, optional): Whether to print results. Defaults to True.
        
    Returns:
        list: A list of port numbers associated with the service.
    """
    try:
        found_ports = []
        common_services = {
            'ftp': 21, 'ssh': 22, 'telnet': 23, 'smtp': 25, 
            'dns': 53, 'http': 80, 'pop3': 110, 'sftp': 115,
            'imap': 143, 'https': 443, 'smb': 445, 'mysql': 3306, 
            'rdp': 3389, 'postgresql': 5432, 'vnc': 5900
        }
        
        # Check if service is in our common services dictionary
        service_lower = service_name.lower()
        for svc, port in common_services.items():
            if service_lower in svc or svc in service_lower:
                found_ports.append(port)
        
        # Try using socket's getservbyname
        try:
            port = socket.getservbyname(service_lower)
            if port not in found_ports:
                found_ports.append(port)
        except (socket.error, OSError):
            pass
            
        if verbose:
            if found_ports:
                console.print(f"[green]Ports for {service_name}:[/green] {', '.join(str(p) for p in found_ports)}")
            else:
                console.print(f"[yellow]No ports found for service: {service_name}[/yellow]")
                
        return found_ports
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return []