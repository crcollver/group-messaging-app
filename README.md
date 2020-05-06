# group-messaging-app

Anonymous group messaging for use inside of your own network.

## Todo

- There may be some bugs as some of this hasn't been thoroughly tested yet.

## Completed

1. Shutdown using ^C
2. Better threading for server.py and client.py

- client.py has a thread dedicated to receiving messages
- server.py has a thread dedicated to accepting clients

3. Send to all users that someone has connected/disconnected.
4. Echo a message to all users connected.
5. Separate version of the app with Tkinter GUI for client.py and/or server.py
6. Keybind to switch to random Python code without disrupting connection. Use HIDE/SHOW command in prompt.

## prompt_toolkit

We now use prompt_toolkit for moving the cursor down when client.py receives a message.
This must be installed in order for client.py to run. Use this command in your terminal:
`pip install prompt_toolkit`
