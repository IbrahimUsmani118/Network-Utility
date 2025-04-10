"""
DNS utilities for network operations.

This module provides functions for DNS operations, including resolving domain names to IP addresses,
performing reverse DNS lookups, and querying various DNS record types like MX, CNAME, NS, etc.
It offers a simple interface for common DNS-related networking tasks with proper error handling.
"""

import socket
try:
    import dns.resolver
    import dns.reversename
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False
from rich.console import Console
from rich.table import Table

console = Console()

def dns_lookup(domain=None, record_type="A"):
    """
    Resolve a domain name to its corresponding IP address(es) or other record types.
    
    Args:
        domain (str, optional): The domain name to resolve. If None, prompts the user for input.
        record_type (str, optional): The DNS record type to query (A, AAAA, MX, CNAME, NS, TXT, etc.). 
                                     Defaults to "A".
    
    Returns:
        list: A list of results corresponding to the requested record type.
        
    Raises:
        dns.resolver.NXDOMAIN: If the domain name does not exist.
        dns.resolver.NoAnswer: If there is no record of the requested type.
        dns.exception.DNSException: For other DNS-related errors.
    """
    if domain is None:
        domain = input("Enter a domain name to lookup: ")
    
    record_type = record_type.upper()  # Ensure upper case for record type
    
    console.print(f"Looking up {record_type} records for [bold]{domain}[/bold]...")
    
    if not HAS_DNSPYTHON:
        # Fallback to socket if dnspython is not available (only supports A records)
        if record_type != "A":
            console.print("[bold red]Error:[/bold red] The 'dnspython' package is required for non-A record lookups.")
            console.print("[bold yellow]Tip:[/bold yellow] Install it using 'pip install dnspython'")
            return None
        
        try:
            ip_addresses = socket.gethostbyname_ex(domain)[2]
            console.print(f"[green]Found {len(ip_addresses)} A record(s) for {domain}:[/green]")
            for ip in ip_addresses:
                console.print(f"  {ip}")
            return ip_addresses
        except socket.gaierror as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            return None
    
    # Use dnspython for more advanced DNS operations
    try:
        answers = dns.resolver.resolve(domain, record_type)
        
        # Create a table for displaying results
        table = Table(title=f"{record_type} Records for {domain}")
        
        if record_type in ("A", "AAAA"):
            table.add_column("IP Address", style="cyan")
            results = [str(rdata) for rdata in answers]
            for result in results:
                table.add_row(result)
        
        elif record_type == "MX":
            table.add_column("Preference", style="magenta")
            table.add_column("Mail Server", style="cyan")
            results = [(rdata.preference, str(rdata.exchange)) for rdata in answers]
            for preference, exchange in results:
                table.add_row(str(preference), exchange)
        
        elif record_type == "NS":
            table.add_column("Nameserver", style="cyan")
            results = [str(rdata.target) for rdata in answers]
            for result in results:
                table.add_row(result)
        
        elif record_type == "CNAME":
            table.add_column("Canonical Name", style="cyan")
            results = [str(rdata.target) for rdata in answers]
            for result in results:
                table.add_row(result)
        
        elif record_type == "TXT":
            table.add_column("Text Value", style="cyan")
            results = [str(rdata) for rdata in answers]
            for result in results:
                table.add_row(result)
        
        elif record_type == "SOA":
            table.add_column("Property", style="magenta")
            table.add_column("Value", style="cyan")
            rdata = answers[0]
            results = [
                ("Primary NS", str(rdata.mname)),
                ("Responsible Person", str(rdata.rname)),
                ("Serial", str(rdata.serial)),
                ("Refresh", f"{rdata.refresh} seconds"),
                ("Retry", f"{rdata.retry} seconds"),
                ("Expire", f"{rdata.expire} seconds"),
                ("Minimum TTL", f"{rdata.minimum} seconds")
            ]
            for property_name, value in results:
                table.add_row(property_name, value)
        
        else:
            # Generic handler for other record types
            table.add_column("Value", style="cyan")
            results = [str(rdata) for rdata in answers]
            for result in results:
                table.add_row(result)
        
        console.print(table)
        
        # Return the raw results
        if record_type == "MX":
            return [(rdata.preference, str(rdata.exchange)) for rdata in answers]
        elif record_type in ("NS", "CNAME"):
            return [str(rdata.target) for rdata in answers]
        else:
            return [str(rdata) for rdata in answers]
    
    except dns.resolver.NXDOMAIN:
        console.print(f"[bold red]Error:[/bold red] The domain {domain} does not exist.")
    except dns.resolver.NoAnswer:
        console.print(f"[bold red]Error:[/bold red] No {record_type} records found for {domain}.")
    except dns.exception.DNSException as e:
        console.print(f"[bold red]DNS Error:[/bold red] {str(e)}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")
    
    return None


def reverse_dns_lookup(ip_address=None):
    """
    Perform a reverse DNS lookup to get the hostname for an IP address.
    
    Args:
        ip_address (str, optional): The IP address to look up. If None, prompts the user for input.
    
    Returns:
        str: The hostname corresponding to the IP address.
        
    Raises:
        socket.herror: If the IP address cannot be resolved to a hostname.
        ValueError: If the input is not a valid IP address.
    """
    if ip_address is None:
        ip_address = input("Enter an IP address for reverse lookup: ")
    
    console.print(f"Performing reverse DNS lookup for [bold]{ip_address}[/bold]...")
    
    try:
        # Verify this is a valid IP address
        try:
            socket.inet_pton(socket.AF_INET, ip_address)
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, ip_address)
            except socket.error:
                raise ValueError("Invalid IP address format")
        
        if HAS_DNSPYTHON:
            # Use dnspython for reverse lookup
            addr = dns.reversename.from_address(ip_address)
            try:
                hostname = str(dns.resolver.resolve(addr, "PTR")[0])
                console.print(f"[green]Hostname for {ip_address}:[/green] {hostname}")
                return hostname
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                console.print(f"[bold yellow]No reverse DNS record found for {ip_address}[/bold yellow]")
                return None
        else:
            # Fallback to socket for reverse lookup
            hostname, _, _ = socket.gethostbyaddr(ip_address)
            console.print(f"[green]Hostname for {ip_address}:[/green] {hostname}")
            return hostname
    
    except socket.herror:
        console.print(f"[bold yellow]No reverse DNS record found for {ip_address}[/bold yellow]")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
    
    return None


def bulk_dns_lookup(domains, record_type="A"):
    """
    Perform DNS lookups for multiple domains.
    
    Args:
        domains (list): A list of domain names to resolve.
        record_type (str, optional): The DNS record type to query. Defaults to "A".
    
    Returns:
        dict: A dictionary mapping each domain to its lookup results.
    """
    if not domains:
        console.print("[bold yellow]Warning:[/bold yellow] No domains provided for bulk lookup")
        return {}
    
    results = {}
    record_type = record_type.upper()
    
    console.print(f"Performing bulk {record_type} record lookup for {len(domains)} domains...")
    
    for domain in domains:
        results[domain] = dns_lookup(domain, record_type)
    
    return results