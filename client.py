import socket

# Server information
server_ip = socket.gethostbyname("vayu.iitd.ac.in")
server_port = 9801

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send the "SendSize" command to the server
client_socket.sendto("SendSize\n\n".encode('utf-8'), (server_ip, server_port))
print("msg sent")

# Receive the size response from the server
data, server_address = client_socket.recvfrom(1024)
print("msg recived")
response = data.decode('utf-8').strip()

# Extract and print the size
if response.startswith("Size:"):
    size = int(response.split(" ")[1])
    print(f"Received size from {server_address}: {size} bytes")

# Close the client socket
client_socket.close()
