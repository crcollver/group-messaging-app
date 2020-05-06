#---------------------------------------------------
# Cameron Collver, Erik Shepard, & Rodolfo Rodriguez
# Anonymous Group Messaging - client-GUI.py
# Client Tkinter script for connecting to server.py
# Uses a default port of 12000 that is unchangeable for now
#
# SOURCES:
# https://www.youtube.com/watch?v=FKlmAkEb40s
# http://net-informations.com/python/net/thread.htm
# https://www.tutorialspoint.com/socket-programming-with-multi-threading-in-python
# https://github.com/effiongcharles/multi_user_chat_application_in_python
#---------------------------------------------------

from __future__ import unicode_literals
import socket
import threading
import tkinter
from tkinter import messagebox
from tkinter import simpledialog

host = socket.gethostbyname(socket.gethostname())
port = 12000
clientSocket = None
username = ""

window = tkinter.Tk()
window.title("Client")

def close_connection():
  """ Handles an explicit closing of the connection """
  if clientSocket is not None:
    clientSocket.sendall("exit".encode("utf-8"))
    clientSocket.close()
  window.destroy()

window.protocol("WM_DELETE_WINDOW", close_connection)

# Top frame to connect
topFrame = tkinter.Frame(window)
lblHost = tkinter.Label(topFrame, text = "Host IP:").pack(side=tkinter.LEFT)
entHost = tkinter.Entry(topFrame)
entHost.pack(side=tkinter.LEFT, padx=(0, 3))
entHost.insert(tkinter.END, host)
btnConnect = tkinter.Button(topFrame, text="Connect", command=lambda : connect())
btnConnect.pack(side=tkinter.LEFT)
topFrame.pack(side=tkinter.TOP, pady=(5, 10))

# Display frame to show all messages
displayFrame = tkinter.Frame(window)
scrollBar = tkinter.Scrollbar(displayFrame)
scrollBar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
tkDisplay = tkinter.Text(displayFrame, height=20, width=60)
tkDisplay.pack(side=tkinter.LEFT, fill=tkinter.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
tkDisplay.tag_config("tag_direct_message", foreground="green")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tkinter.TOP)

# bottom frame for sending a message
bottomFrame = tkinter.Frame(window)
tkMessage = tkinter.Text(bottomFrame, height=2, width=60)
tkMessage.pack(side=tkinter.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: get_msg(tkMessage.get("1.0", tkinter.END))))
bottomFrame.pack(side=tkinter.BOTTOM)

def connect():
  """ Connect to specified server based on runtime arguments """
  global clientSocket, host, port
  if len(entHost.get()) > 1:
    host = entHost.get() # change host to user specified host
  try:
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((host, port))
    select_username()
    if clientSocket is not None and username: # as long as the socket still exists and there is a valid username
      # Create the thread that will receive messages only after username is established
      # This thread will be killed once the socket is closed
      RECEIVE_THREAD = threading.Thread(target=receive_message)
      RECEIVE_THREAD.daemon = True
      RECEIVE_THREAD.start()
  except Exception as e:
    tkinter.messagebox.showerror(title="ERROR", message=f"Unable to connect to host: {host}:{port}. Server may be unavailable.")


def select_username():
  """ Once a connection is established, make user select a username for this session """
  global username, clientSocket
  while True:
    try:
      username = simpledialog.askstring("Setup", "Enter a username...", parent=window)
      if username is not None:
        clientSocket.sendall(username.encode("utf-8"))
        server_res = clientSocket.recv(1024)  #sending potential username to server
        # checking for byte message that server sent back should be fine for our app
        tkDisplay.config(state=tkinter.NORMAL)
        if (server_res.decode() == "username_avail"):
          tkDisplay.insert(tkinter.END, f"Great this username is available!\n<@{username}> will be your username for this session.")
          tkMessage.config(state=tkinter.NORMAL)     # set the message box to an enabled state to capture username
          entHost.config(state=tkinter.DISABLED)     # Disable host input box once a connection has been made
          btnConnect.config(state=tkinter.DISABLED)  # Disable connect button once a connection has been made
          break
        tkDisplay.insert(tkinter.END, f"The username {username} seems to be taken, lets try again.\n")
        tkDisplay.config(state=tkinter.DISABLED)
      else:
        clientSocket.close()
        clientSocket = None
        break # return to the main window and have user reconnect
    except ConnectionAbortedError:
      tkinter.messagebox.showerror(title="SERVER ERROR", message=f"Server on {host}:{port} has shutdown unexpectedly.")
      break
  

def receive_message():
  """ Handles the receiving of server messages, without blocking main thread """
  global clientSocket
  while True:
    try:
      server_msg = clientSocket.recv(1024)
      if not server_msg:
        break
      tkDisplay.config(state=tkinter.NORMAL)
      if server_msg.decode().startswith("From <@"): # if message is a direct message, color it green
        tkDisplay.insert(tkinter.END, f"\n{server_msg.decode()}", "tag_direct_message")
      else:
        tkDisplay.insert(tkinter.END, f"\n{server_msg.decode()}")
      tkDisplay.config(state=tkinter.DISABLED)
      tkDisplay.see(tkinter.END)

    # throws this error when server shuts down with clients still connected
    except ConnectionResetError:
      tkinter.messagebox.showerror(title="SERVER ERROR", message=f"Server on {host}:{port} has shutdown unexpectedly.")
      break
    # throws this error when user types exit, suppresses it
    except ConnectionAbortedError:
      break
  
  clientSocket.close()
  window.destroy()


def get_msg(msg):
  """ Get the user message from the message text box """
  msg = msg.replace('\n', '')

  # if this is a regular message, print it to the window
  # otherwise user is sending potential user name so we do not display
  tkDisplay.config(state=tkinter.NORMAL) # cannot insert into a window that is disabled
  tkDisplay.insert(tkinter.END, f"\n<@{username}>: {msg}", "tag_your_message")
  tkDisplay.config(state=tkinter.DISABLED)  # disable window once insert it performed
  tkDisplay.see(tkinter.END)  # scroll if not enough room in window

  tkMessage.delete('1.0', tkinter.END)  # remove text in message window
  send_message(msg)


def send_message(msg):
  """ Sends the message to server on the main thread """
  clientSocket.sendall(msg.encode("utf-8"))
  if msg == "exit":
    close_connection()

window.mainloop()
