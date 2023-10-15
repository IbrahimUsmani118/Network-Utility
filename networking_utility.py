# import necessary modules
from rich.console import Console
import ipaddress
import socket
import requests

console = Console()

def extractData():
    url = input("Enter a URL to extract data from (e.g. http://www.google.com): ")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        console.print(data)
    except requests.exceptions.HTTPError as e:
        console.print("HTTP Error:", e)
    except requests.exceptions.ConnectionError:
        console.print("Connection Error: Could not connect to", url)
    except requests.exceptions.Timeout:
        console.print("Timeout Error: Request timed out")
    except requests.exceptions.RequestException as e:
        console.print("Error:", e)

def subnetting():
    ip_address = input("Enter an IP address to subnet (e.g. 192.168.0.0): ")
    mask = input("Enter the subnet mask (e.g. 24): ")
    try:
        network = ipaddress.ip_network(ip_address+'/'+mask, strict=False)
        console.print("Network address:", network.network_address)
        console.print("Broadcast address:", network.broadcast_address)
        console.print("Number of hosts:", network.num_addresses)
    except ValueError:
        console.print("Invalid IP address or mask")

def readIPAddress():
    try:
        link = input("Enter a URL to read its IP address: ")
        ip_address = socket.gethostbyname(link)
        console.print(ip_address)
    except socket.gaierror:
        console.print("Could not resolve IP address for", link)

def main():
    while True:
        console.print("\nSelect a networking process:")
        console.print("1. Read IP Address")
        console.print("2. Subnetting")
        console.print("3. Extract Data from a Network")
        console.print("4. Quit")
        response = input("Enter the number of your selection: ")
        
        if response == "1":
            readIPAddress()
        elif response == "2":
            subnetting()
        elif response == "3":
            extractData()
        elif response == "4":
            print("Exiting program...")
            break
        else:
            console.print("Invalid selection")

if __name__ == "__main__":
    main()
