import socket
import time,threading,hashlib

def receive_data(sock):
    global offset_data
    global offset_received
    global stop_thread
    while not stop_thread:
        try:
            sock.settimeout(.05)
            data, address = sock.recvfrom(2048)
            response = data.decode('utf-8').split('\n')
            offset = int(response[0].split(" ")[1])
            offset_received[(offset)//1448] = True
            add_to_string = False
            string = ""
            for substring in response:
                if add_to_string:
                    string += substring+'\n'
                if not add_to_string and substring == '':
                    add_to_string = True
            offset_data[(offset)//1448] = string[:-1]
            time_run = (time.time()-start_time)*1000
            # receive_time[offset] = time_run
            receive_time.write(f"{offset}\t{time_run:.2f}\n")
            # print(f"{offset//1448} Received")
        except socket.timeout:
            continue

# Server information
server_ip = "127.0.0.1"
server_port = 9801

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
size_to_receive = 0

while (size_to_receive==0):
    # Send the "SendSize" command to the server
    udp_socket.sendto("SendSize\nReset\n\n".encode('utf-8'), (server_ip, server_port))

    # Receive the size response from the server
    try:
        udp_socket.settimeout(.5)
        data, server_address = udp_socket.recvfrom(1024)
        response = data.decode('utf-8').strip()

        # Extract and print the size
        if response.startswith("Size:"):
            size = int(response.split(" ")[1])
            size_to_receive = size
            print(f"Received size : {size_to_receive} bytes")
    except socket.timeout:
        print("Resending msg to capture size")

no_of_request = (size_to_receive+1448-1)//1448
offset_received = [False]*no_of_request
offset_data = [""]*no_of_request
print("no of request: ",no_of_request)
receive_time = open("receive.txt","w")
request_time = open("request.txt","w")


first_False = 0
time.sleep(.05)
start_time = time.time()
while (first_False < no_of_request):
    k = 0
    frontier = []
    while (len(frontier)!=10 and ((first_False+k)<no_of_request)):
        if offset_received[first_False+k] == False:
            frontier.append(first_False+k)
        k+=1
    
    if len(frontier)==0:
        break

    for offset_number in frontier:
        if offset_number == no_of_request-1:
            numbytes = size_to_receive%1448
            if numbytes == 0:
                numbytes = 1448
        else:
            numbytes = 1448
        udp_socket.sendto(f"Offset: {offset_number*1448}\nNumBytes: {numbytes}\n\n".encode('utf-8'), (server_ip, server_port))
        time_run = (time.time()-start_time)*1000
        # if offset_number*1448 in request_time:
        #     request_time[offset_number*1448].append(str(time_run))
        # else:
        #     request_time[offset_number*1448] = [str(time_run)]
        request_time.write(f"{offset_number*1448}\t{time_run:.2f}\n")

    receive_thread = threading.Thread(target=receive_data, args=(udp_socket, ))
    stop_thread = False
    receive_thread.start()
    time.sleep(.05)
    stop_thread = True
    receive_thread.join()

    has_false = False
    for offset_number in frontier:
        if offset_received[offset_number] == False:
            first_False = offset_number
            has_false = True
            break
    if not has_false:
        first_False = frontier[-1]+1


full_data = ''.join(offset_data)
md5_hash = hashlib.md5()
md5_hash.update(full_data.encode('utf-8'))
md5_hex = md5_hash.hexdigest()
print(md5_hex)
udp_socket.sendto(f"Submit: 2021CS10121@lol\nMD5: {md5_hex}\n\n".encode('utf-8'), (server_ip, server_port))
udp_socket.settimeout(.5)
data, server_address = udp_socket.recvfrom(1024)
response = data.decode('utf-8').strip()
print(response)



# Close the client socket
udp_socket.close()
