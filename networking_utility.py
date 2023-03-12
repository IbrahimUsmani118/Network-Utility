# import necessary modules
import ipaddress
import socket
import requests

def extractData():
    url = input("Enter a URL to extract data from (e.g. http://www.google.com): ")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.text
        print(data)
    except requests.exceptions.HTTPError as e:
        print("HTTP Error:", e)
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to", url)
    except requests.exceptions.Timeout:
        print("Timeout Error: Request timed out")
    except requests.exceptions.RequestException as e:
        print("Error:", e)

def subnetting():
    ip_address = input("Enter an IP address to subnet (e.g. 192.168.0.0): ")
    mask = input("Enter the subnet mask (e.g. 24): ")
    try:
        network = ipaddress.ip_network(ip_address+'/'+mask, strict=False)
        print("Network address:", network.network_address)
        print("Broadcast address:", network.broadcast_address)
        print("Number of hosts:", network.num_addresses)
    except ValueError:
        print("Invalid IP address or mask")

def readIPAddress():
    try:
        link = input("Enter a URL to read its IP address: ")
        ip_address = socket.gethostbyname(link)
        print(ip_address)
    except socket.gaierror:
        print("Could not resolve IP address for", link)

def main():
    while True:
        print("\nSelect a networking process:")
        print("1. Read IP Address")
        print("2. Subnetting")
        print("3. Extract Data from a Network")
        print("4. Quit")
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
            print("Invalid selection")

if __name__ == "__main__":
    main()
