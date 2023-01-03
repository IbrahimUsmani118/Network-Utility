# import necessary modules
import ipaddress
import socket
import requests

while True:
    # This method extracts the server data from a website
    def extractData():
        url = input("Enter a URL which you would like to send a HTTP GET request to the web server(e.g http://www.google.com): ")
        # send a HTTP GET request to the web server
        response = requests.get(url)
        
        # check the status code of the response
        if response.status_code == 200:
            # extract the data from the response
            data = response.text
            print(data)
            
    # This method is the method used for subnetting by entering a mask and an IP address
    def subnetting():
        # Prompt the user for the IP address and mask to use for subnetting
        ip_address = input('Enter the IP address to use for subnetting: ')
        mask = input('Enter the subnet mask to use for subnetting: ')
        
        # Create a network object using the provided IP address and mask
        network = ipaddress.ip_network(ip_address + '/' + mask, strict=False)
    
        # Print the network address, broadcast address, and number of hosts for the network
        print('Network address:', network.network_address)
        print('Broadcast address:', network.broadcast_address)
        print('Number of hosts:', network.num_addresses)
        
    # This method is used to read an IP address of any base URL/link
    def readIPAddress():
        try:
            link = input("Enter a URL: ")
            ip_address = socket.gethostbyname(link)
            print(ip_address)
        except socket.gaierror:
            print("Could not resolve IP address for ", link)
            
    # Main method to call upon the functions based on user's selection
    def main():
        print("List of processes:")
        print("1. Read IP Address")
        print("2. Subnetting")
        print("3. Extract Data from a Network")
        response = input("What networking process would you like to run(Enter a number or 'close program' to exit): ")
        
        if response == "1":
            readIPAddress()
        elif response == "2":
            subnetting()
        elif response == "3":
            extractData()
        elif response == "close program":
            quit()
    
main()