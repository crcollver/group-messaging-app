# group-messaging-app
Anonymous group messaging for use inside of your own network.

## Todo
* Shutting down gracefully could probably be done better.
* Echo messages to all users.
* Send to all users that someone has connected/disconnected.

## Completed
1. Shutdown using ^C
2. Better threading for server.py and client.py
* client.py has a thread dedicated to receiving messages
* server.py has a thread dedicated to accepting clients

## prompt_toolkit
We now use prompt_toolkit for moving the cursor down when client.py receives a message.
This must be installed in order for client.py to run.  Use this command in your terminal:
`pip install prompt_toolkit`
