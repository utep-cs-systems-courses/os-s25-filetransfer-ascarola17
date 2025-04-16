#! /usr/bin/env python3

import socket, sys, re, os, struct
sys.path.append("./lib")  # for params
import params

switchesVarDefaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-?', '--usage'), "usage", False),
)

progname = "fileServer"
paramMap = params.parseParams(switchesVarDefaults)

listenPort = paramMap['listenPort']
listenAddr = ''  # all interfaces

if paramMap['usage']:
    params.usage()

# Set up listening socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(5)  # allow up to 5 pending connections
print(f" Server listening on port {listenPort}...")

# Function to handle one client
def handle_client(conn, addr):
    print(f"Child process handling {addr}")

    try:
        # Step 1: Receive filename length in 4 bytes 
        filename_len_bytes = conn.recv(4)
        if not filename_len_bytes:
            print("Didn't receive filename length.")
            return

        #Unpack the filename bytes (!I converts bytes to int)
        filename_len = struct.unpack('!I', filename_len_bytes)[0]

        # Step 2: Receive filename
        filename = conn.recv(filename_len).decode()
        print(f"Receiving file: {filename}")

        # Step 3: Receive file data length
        file_data_len_bytes = conn.recv(4)
        file_data_len = struct.unpack('!I', file_data_len_bytes)[0]

        # Step 4: Receive file data in chunks until we get the whole thing
        received_data = b''
        while len(received_data) < file_data_len:
            chunk = conn.recv(min(1024, file_data_len - len(received_data)))
            if not chunk:
                break
            received_data += chunk

        # Step 5: Write file data to new file in the server
        with open(filename, 'wb') as f:
            f.write(received_data)

        print(f"✅ Saved file '{filename}' ({file_data_len} bytes)")

        #Send acknowledgement to client
        conn.sendall(b"File received successfully.\n")

    except Exception as e:
        #Close the connection and exit the child process
        print(f"⚠️ Error while handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"Connection to {addr} closed")
        os._exit(0)  # ensure child exits

# Server main loop — accept and fork
while True:
    conn, addr = s.accept()
    print(f"Connection from {addr}")

    #Make new process for each client
    pid = os.fork()
    if pid == 0:
        # In child process
        s.close()  # child doesn't need the listening socket
        handle_client(conn, addr)
    else:
        # In parent process
        conn.close()  # parent doesn't need the client socket
