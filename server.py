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
# Allows us to run our server with host & port arguments
parser = argparse.ArgumentParser(description = "Multi-threaded server")

# first argument is --host, expecting 0 or 1 string arguments
parser.add_argument('--host', metavar = 'host', type = str, nargs = '?', default = "localhost")
# second argument is --port, expecting 0 or 1 integer arguments
parser.add_argument('--port', metavar = 'port', type = int, nargs = '?', default = 12000)
args = parser.parse_args()

print(f"Running server on: {args.host} on port {args.port}")


serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # eliminates error when server is ran again immediately after a close

try:
  serverSocket.bind((args.host, args.port))
  serverSocket.listen(5) # allows 5 unaccepted connections before refusing new ones
except Exception as bind_error:
  raise SystemExit(f"Could not bind server on: {args.host} on port {args.port}.  Error: {bind_error}")


def new_client(client, connection, userName):
  """
  Handle new client.  Closes connection if client types "exit".

  PARAMS:
  client -- socket object for a new client
  connection -- address information for new client (ip, port)
  """
  ip = connection[0]
  port = connection[1]
  print(f"New connection made from: {ip} with {port}")

  while True:
    msg = client.recv(1024)
    if(msg.decode() == "exit"):
      break
    print(f"Client's message: {msg.decode()}")
    reply = f"Server received from {userName}:  {msg.decode()}"
    client.sendall(reply.encode("utf-8"))
  print(f"Client from: {ip} with port {port} has disconnected.")
  client.close()


userName= ["Admin"] # Creates an active list of usernames being used. Adds "Admin" by default to prevent use of it.
while True: #checks client username suggestion against list of active userNames.
  try:
    client, ip = serverSocket.accept()
    print("connection recieved, assigning username\n")
    while True:
        msg = client.recv(1024)
        if msg.decode() in userName:
            msg = "True"
            client.sendall(msg.encode())
        else:
            userName.insert(0,msg.decode())
            print("username "+msg.decode()+" is being assigned.")
            msg = "False"
            client.sendall(msg.encode())
            break

    threading._start_new_thread(new_client, (client, ip, userName[0]))
  except KeyboardInterrupt:
    print("Cleaning up threads and shutting down")
    break
  except Exception as thread_error:
    print(f"Error creating thread: {thread_error}")

serverSocket.close()
