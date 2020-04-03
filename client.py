#---------------------------------------------------
# Cameron Collver, Erik Shepard, & Rodolfo Rodriguez
# Anonymous Group Messaging - client.py
# Client script for connecting to server.py
#
# SOURCES:
# https://www.youtube.com/watch?v=FKlmAkEb40s
# http://net-informations.com/python/net/thread.htm
# https://www.tutorialspoint.com/socket-programming-with-multi-threading-in-python
#---------------------------------------------------

import socket
import argparse # CLI parsing module

# Allows for us to run our client with host & port arguments
parser = argparse.ArgumentParser(description = "Client for chat server.")

# first argument is --host, expecting 0 or 1 string arguments
# default gets the network IP of machine you are currently running on
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostbyname(socket.gethostname()))
# second argument is --port, expecting 0 or 1 integer arguments
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 12000)
args = parser.parse_args()

print(f"Connecting to server: {args.host} on port {args.port}")
try:
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  clientSocket.connect((args.host, args.port))
except Exception as connect_error:
  raise SystemExit(f"Failed to connect to host: {args.host} on port: {args.port}.  Error: {connect_error}")

while True: #Allows user to assign their username to the server. ensuring no duplicates.
    msg=input("Select a Username!")
    clientSocket.sendall(msg.encode("utf-8"))
    server_msg=clientSocket.recv(1024)  #sending potential username to server.

    if (server_msg.decode() == "False") :# Might use distutils.util.strtobool(server_msg.decode())- this should intepret the string as a bool.
        print ("Great this username is available.\n "+msg+" will be your username for this session.")
        break
    print("The username "+msg+" seems to be taken, lets try again.")

while True:
  msg = input("Send to the server: ")
  clientSocket.sendall(msg.encode("utf-8")) # allows for all types of unicode characters to be sent

  # if user wants to exit
  if(msg == "exit"):
    print("Goodbye")
    break

  server_msg = clientSocket.recv(1024)
  print(f"Server response: {server_msg.decode()}")

clientSocket.close()
