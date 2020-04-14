#---------------------------------------------------
# Cameron Collver, Erik Shepard, & Rodolfo Rodriguez
# Anonymous Group Messaging - server.py
# Multi-threaded TCP server to echo back messages to
#   all connected clients.
#
# SOURCES:
# https://www.youtube.com/watch?v=FKlmAkEb40s
# http://net-informations.com/python/net/thread.htm
# https://www.tutorialspoint.com/socket-programming-with-multi-threading-in-python
#---------------------------------------------------

# importing as full modules to make code easier to read
import socket
import argparse # CLI parsing module
import threading
from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout

# Allows us to run our server with port arguments
parser = argparse.ArgumentParser(description = "Multi-threaded server")

# argument is --port, expecting 0 or 1 integer arguments
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 12000)
args = parser.parse_args()

host_ip = socket.gethostbyname(socket.gethostname()) # gets network IP of localhost so others can connect

print(f"Running server on {host_ip}:{args.port}")

serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # eliminates error when server is ran again immediately after a close

try:
  serverSocket.bind(("", args.port))
  serverSocket.listen(5) # allows 5 unaccepted connections before refusing new ones
except Exception as bind_error:
  raise SystemExit(f"Could not bind server on {args.host}:{args.port}.  Error: {bind_error}")

usernames= {} # dictionary of client socket object, username pairs for easy removal during a disconnect
              # client socket object should never change for username's duration, allowing us to use it as a key
connections = [] # list of active connections


def accept_connections():
  """Handling thread for accepting incoming client connections"""
  while True:
    client, ip = serverSocket.accept()
    try:
      # uses another daemon thread for client connections for easy server termination
      CLIENT_THREAD = threading.Thread(target=new_client, args=(client, ip))
      CLIENT_THREAD.daemon = True
      CLIENT_THREAD.start()
    except Exception as thread_error:
      print(f"Error creating thread: {thread_error}")


def new_client(client, info):
  """
  Handle new client.  Closes connection if client types "exit".

  PARAMS:
  client -- socket object for a new client
  connection -- address information for new client (ip, port)
  """
  ip = info[0]
  port = info[1]
  print(f"New connection made from {ip}:{port}, assigning username...")

  # handles username selection and adds it to list of usernames
  while True:
    msg = client.recv(1024)
    if not msg:
      break
    if msg.decode() in usernames:
      msg = "username_taken"
      client.sendall(msg.encode())
    else:
      usernames[client] = msg.decode()
      print("Username " + msg.decode() + " is being assigned.")
      msg = "username_avail"
      client.sendall(msg.encode("utf-8"))

      if connections:
        for connection in connections:
          connection.sendall(f"<@{usernames[client]}> has joined the server!".encode("utf-8"))
      connections.append(client)
      break
  
  # handles message sending and echoing
  while True:
    msg = client.recv(1024)
    if not msg:
      break
    if(msg.decode() == "exit"):
      break
    reply = msg.decode()
    # print(f"<@{usernames[client]}>: {reply}")
    for connection in connections:
      if connection != client:  # Do not send the message to the client that sent it
        connection.sendall(f"<@{usernames[client]}>: {reply}".encode("utf-8"))

  print(f"Client from {ip}:{port} with username {usernames[client]} has disconnected.")
  connections.remove(client)
  if connections:
    for connection in connections:
      connection.sendall(f"<@{usernames[client]}> has left the server, bye!".encode("utf-8"))
  del usernames[client]
  client.close()


""" Main Thread that allows for interruption  """
try:
  # create a Daemon thread for easy server exit
  # we are not writing to any system files, so resources should be freed immediately
  SOCKET_ACCEPT_THREAD = threading.Thread(target=accept_connections)
  SOCKET_ACCEPT_THREAD.daemon = True
  SOCKET_ACCEPT_THREAD.start()

  # spin until interrupted (^C) or "exit" command is given
  while True:
    pass

except KeyboardInterrupt:
  print("Cleaning up threads and shutting down...")
except Exception as thread_error:
  print(f"Error creating thread: {thread_error}")

serverSocket.close()
