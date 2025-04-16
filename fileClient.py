#! /usr/bin/env python3

import socket, sys, re, os, struct
sys.path.append("./lib")  # make sure params.py is in ./lib
import params

# Debug args during dev
#print("ARGS:", sys.argv)

# Command-line flag defaults
switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-?', '--usage'), "usage", False),
    (('-f', '--file'), 'file', "none"),  # File to send
)


progname = "fileClient"
paramMap = params.parseParams(switchesVarDefaults)

# Error testing
#if paramMap["usage"]:
#    params.usage()

# Validate and extract filename (Get it from the command line)
filename = paramMap["file"]
if not filename:
    print("You must provide a file using -f")
    print("Usage: python3 fileClient.py -f test.txt")
    sys.exit(1)

# Parse server IP and port to connect to the host
try:
    serverHost, serverPort = re.split(":", paramMap["server"])
    serverPort = int(serverPort)
except:
    print(f"Invalid server format: {paramMap['server']} (expected format IP:PORT)")
    sys.exit(1)

# Open socket and connect to the server 
s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        print(f"Creating socket: af={af}, type={socktype}, proto={proto}")
        s = socket.socket(af, socktype, proto)
        s.connect(sa)
        break
    except socket.error as msg:
        print(f"Connection error: {msg}")
        s = None
        continue
    #break

if s is None:
    print("Could not open socket")
    sys.exit(1)

###
# get only the filename 
filename_only = os.path.basename(filename)

#Try and open and read the file to send 
try:
    with open(filename, 'rb') as f:
        file_data = f.read()
except FileNotFoundError:
    print(f" File not found: {filename}")
    s.close()
    sys.exit(1)

# Send framed message
# 1. Filename length in bytes (4 bytes)
s.sendall(struct.pack('!I', len(filename_only)))
# 2. Filename
s.sendall(filename_only.encode())
# 3. File data length (4 bytes)
s.sendall(struct.pack('!I', len(file_data)))
# 4. File data
s.sendall(file_data)

print(f"Sent file '{filename_only}' ({len(file_data)} bytes)")

# receive any response from server to make sure it worked 
s.shutdown(socket.SHUT_WR)
while True:
    data = s.recv(1024)
    if not data:
        break
    print("Received from server:", data.decode())

print("Connection closed.")
s.close()
