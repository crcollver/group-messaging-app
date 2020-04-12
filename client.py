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
import threading
from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout

# Allows for us to run our client with host & port arguments
parser = argparse.ArgumentParser(description = "Client for chat server.")

# first argument is --host, expecting 0 or 1 string arguments
# default gets the network IP of machine you are currently running on
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = socket.gethostbyname(socket.gethostname()))
# second argument is --port, expecting 0 or 1 integer arguments
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 12000)
args = parser.parse_args()

""" Connect to specified server based on runtime arguments """
print(f"Connecting to server at {args.host}:{args.port}")
try:
  clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  clientSocket.connect((args.host, args.port))
except Exception as connect_error:
  raise SystemExit(f"Failed to connect to host at {args.host}:{args.port}.  Error: {connect_error}")


""" Once a connection is established, make user select a username for this session """
while True:
  try:
    msg = input("Select a Username>")
    clientSocket.sendall(msg.encode("utf-8"))
    server_msg = clientSocket.recv(1024)  #sending potential username to server.

    # checking for byte message that server sent back should be fine for our app
    if (server_msg.decode() == "username_avail") :  # Might use distutils.util.strtobool(server_msg.decode())- this should intepret the string as a bool.
        print ("Great this username is available.\n " + msg + " will be your username for this session.")
        break
    print("The username " + msg + " seems to be taken, lets try again.")
  except ConnectionAbortedError:
    print(f"Server on {args.host}:{args.port} has shutdown unexpectedly, type 'exit' to exit or close your terminal window.")


def receive_message():
  """ Handles the receiving of server messages, without blocking main thread """
  while True:
    try:
      server_msg = clientSocket.recv(1024)
      print(f"{server_msg.decode()}")
      if not server_msg:
        break
    # throws this error when server shuts down with clients still connected
    except ConnectionResetError:
      print(f"Server on {args.host}:{args.port} has shutdown unexpectedly, type 'exit' to exit or close your terminal window.")
      break
    # throws this error when user types exit
    except ConnectionAbortedError:
      break


""" Main thread that spins on user input """
try:
  RECEIVE_THREAD = threading.Thread(target=receive_message)
  RECEIVE_THREAD.start()
except Exception as thread_error:
  print(f"Error creating thread: {thread_error}")

while True:
  try:
    # Print statements in RECEIVE_THREAD should not disturb input of client
    with patch_stdout():
        msg = prompt(">")
    clientSocket.sendall(msg.encode("utf-8")) # allows for all types of unicode characters to be sent

    # if user wants to exit with command
    if(msg == "exit"):
      print(f"Disconnecting from {args.host}:{args.port}")
      break
  except ConnectionResetError:
    break
  except KeyboardInterrupt:
    # if user wants to exit using ^C
    clientSocket.sendall("exit".encode("utf-8"))
    print(f"Disconnecting from {args.host}:{args.port}.")
    break

clientSocket.close()
