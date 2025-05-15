"""
Web utilities for network operations.

This module provides functions for web operations, including extracting data
from web pages and testing connection speeds. It offers a simple interface for
common web-related networking tasks with proper error handling.
"""

import requests
import time
import os
import json
from urllib.parse import urlparse
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()

def extract_web_data(url=None):
    """
    Extract and display data from a web page.
    
    Args:
        url (str, optional): The URL to extract data from. If None, prompts the user for input.
        
    Returns:
        str: The content of the web page.
        
    Raises:
        requests.exceptions.RequestException: If any request-related error occurs.
    """
    if url is None:
        url = input("Enter a URL to extract data from (e.g. http://www.google.com): ")
    
    # Add http:// prefix if missing
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    try:
        with console.status(f"[bold green]Fetching data from {url}...[/bold green]"):
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        
        data = response.text
        
        # Print header information
        console.print("\n[bold]Response Headers:[/bold]")
        for key, value in response.headers.items():
            console.print(f"[cyan]{key}:[/cyan] {value}")
        
        # Print content preview
        console.print("\n[bold]Content Preview:[/bold]")
        preview = data[:500] + "..." if len(data) > 500 else data
        console.print(preview)
        
        # Get content length
        content_length = len(data)
        console.print(f"\nTotal content length: {content_length} characters")
        
        return data
    
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]HTTP Error:[/bold red] {e}")
    except requests.exceptions.ConnectionError:
        console.print(f"[bold red]Connection Error:[/bold red] Could not connect to {url}")
    except requests.exceptions.Timeout:
        console.print(f"[bold red]Timeout Error:[/bold red] Request timed out")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    
    return None

def speed_test(test_url="https://httpbin.org/stream-bytes/", download_size=1000000, upload_size=500000):
    """
    Test download and upload speeds.
    
    Args:
        test_url (str, optional): Base URL for speed testing. Defaults to "https://httpbin.org/stream-bytes/".
        download_size (int, optional): Size in bytes for download test. Defaults to 1000000 (1MB).
        upload_size (int, optional): Size in bytes for upload test. Defaults to 500000 (0.5MB).
        
    Returns:
        dict: A dictionary containing speed test results (download_speed, upload_speed, latency).
        
    Raises:
        requests.exceptions.RequestException: If any request-related error occurs.
    """
    results = {
        'download_speed': None,  # in Mbps
        'upload_speed': None,    # in Mbps
        'latency': None          # in ms
    }
    
    try:
        # Test latency
        console.print("[bold]Testing latency...[/bold]")
        start_time = time.time()
        requests.get("https://httpbin.org/get", timeout=10)
        latency = (time.time() - start_time) * 1000  # Convert to ms
        results['latency'] = round(latency, 2)
        console.print(f"Latency: {results['latency']} ms")
        
        # Download speed test
        console.print("\n[bold]Testing download speed...[/bold]")
        download_url = f"{test_url}{download_size}"
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]Downloading...", total=100)
            
            start_time = time.time()
            response = requests.get(download_url, stream=True, timeout=30)
            
            # Ensure download is actually completed
            content_length = 0
            for chunk in response.iter_content(chunk_size=1024):
                content_length += len(chunk)
                progress.update(task, completed=min(100, int(content_length / download_size * 100)))
            
            download_time = time.time() - start_time
        
        # Calculate speed in Mbps (megabits per second)
        download_speed = (download_size * 8 / 1000000) / download_time if download_time > 0 else 0
        results['download_speed'] = round(download_speed, 2)
        console.print(f"Download Speed: {results['download_speed']} Mbps")
        
        # Upload speed test
        console.print("\n[bold]Testing upload speed...[/bold]")
        
        # Generate random data for upload
        upload_data = os.urandom(upload_size)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]Uploading...", total=100)
            
            start_time = time.time()
            response = requests.post(
                "https://httpbin.org/post", 
                files={"file": ("test.bin", upload_data)},
                timeout=30
            )
            progress.update(task, completed=100)
            
            upload_time = time.time() - start_time
        
        # Calculate speed in Mbps (megabits per second)
        upload_speed = (upload_size * 8 / 1000000) / upload_time if upload_time > 0 else 0
        results['upload_speed'] = round(upload_speed, 2)
        console.print(f"Upload Speed: {results['upload_speed']} Mbps")
        
        # Summary
        console.print("\n[bold green]Speed Test Results:[/bold green]")
        console.print(f"Latency: {results['latency']} ms")
        console.print(f"Download Speed: {results['download_speed']} Mbps")
        console.print(f"Upload Speed: {results['upload_speed']} Mbps")
        
        return results
    
    except requests.exceptions.HTTPError as e:
        console.print(f"[bold red]HTTP Error:[/bold red] {e}")
    except requests.exceptions.ConnectionError as e:
        console.print(f"[bold red]Connection Error:[/bold red] {e}")
    except requests.exceptions.Timeout:
        console.print(f"[bold red]Timeout Error:[/bold red] Request timed out")
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"[bold red]Unexpected Error:[/bold red] {str(e)}")
    
    return results