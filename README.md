# group-messaging-app
Anonymous group messaging for use inside of your own network.

## Todo
* Shutting down gracefully could probably be done better.
* Echo messages to all users.
* To have safe multi-threading, we should probably implement mutex locks when deleting from the connections list and usernames dictionary found in server.py.
* There may be some bugs as some of this hasn't been thoroughly tested yet.

## Completed
1. Shutdown using ^C
2. Better threading for server.py and client.py
* client.py has a thread dedicated to receiving messages
* server.py has a thread dedicated to accepting clients
3. Send to all users that someone has connected/disconnected.

## prompt_toolkit
We now use prompt_toolkit for moving the cursor down when client.py receives a message.
This must be installed in order for client.py to run.  Use this command in your terminal:
`pip install prompt_toolkit`
