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

import os
import socket
import argparse # CLI parsing module
import threading
from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout


#Cache to allow for disguise screen wipe.
discache= ""
Hflag = False
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


def receive_message():
  global discache
  global Hflag
  """ Handles the receiving of server messages, without blocking main thread """
  while True:
    try:
      server_msg = clientSocket.recv(1024)
      if Hflag == False:
        print(f"{server_msg.decode()}")
      discache =discache + server_msg.decode() + "\n"
      if not server_msg:
        break
    # throws this error when server shuts down with clients still connected
    except ConnectionResetError:
      print(f"Server on {args.host}:{args.port} has shutdown unexpectedly, type 'exit' to exit or close your terminal window.")
      break
    # throws this error when user types exit
    except ConnectionAbortedError:
      break


""" Once a connection is established, make user select a username for this session """
while True:
  try:
    # In case we plan to have output print above this prompt
    with patch_stdout():
      username = prompt('Select a username\n>')
    clientSocket.sendall(username.encode("utf-8"))
    server_res = clientSocket.recv(1024)  #sending potential username to server.

    # checking for byte message that server sent back should be fine for our app
    if (server_res.decode() == "username_avail") :  # Might use distutils.util.strtobool(server_msg.decode())- this should intepret the string as a bool.
        print (f"Great this username is available.\n<@{username}> will be your username for this session.")
        break
    print(f"The username {username} seems to be taken, lets try again.")
  except ConnectionAbortedError:
    print(f"Server on {args.host}:{args.port} has shutdown unexpectedly, type 'exit' to exit or close your terminal window.")


""" Main thread that spins on user input """
try:
  # Create the thread that will receive messages only after username is established
  # This thread will be killed once the socket is closed
  RECEIVE_THREAD = threading.Thread(target=receive_message)
  RECEIVE_THREAD.start()
except Exception as thread_error:
  print(f"Error creating thread: {thread_error}")

while True:
  try:
    # Print statements in RECEIVE_THREAD should not disturb input of client
    with patch_stdout():
        msg = prompt(f"<@{username}>: ")
    #Checks if HIDE command is sent. if not caches message for later use when hiding.
    if msg == "HIDE":
      Hflag = True
      os.system("CLS")
      f = open("Junk Code.txt","r")
      print(f.read())
      f.close()
      while Hflag :
        if input() == "SHOW":
          os.system("CLS")
          print(discache)
          Hflag = False
    else :
      discache = discache + f"<@{username}>: " +msg +"\n"
    #end of disguise
    if msg !="HIDE":
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
