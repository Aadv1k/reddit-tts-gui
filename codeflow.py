import random
import socket
import sys
import json
import praw
import os


def auth():
    scopes = ['read']
    reddit = praw.Reddit(
        redirect_uri="http://localhost:8080",
        user_agent="obtain_refresh_token/v0 by u/bboe",
        client_id="LYQy5q5ICwT-QaTY2hcCow",
        client_secret="uvk6k7CGGgVIRqg40AfGlB_EC0FOtQ",
    )

    state = str(random.randint(0, 65000))

    if os.path.isfile('token.json'):
        with open('token.json', 'r') as file:
            token = json.loads(file.read())
        return token

    else:
        url = reddit.auth.url(scopes, state, "permanent")
        print(f"Now open this url in your browser: {url}")

        client = receive_connection()
        data = client.recv(1024).decode("utf-8")
        param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
        params = {
            key: value for (key, value) in [token.split("=") for token in param_tokens]
        }

        refresh_token = reddit.auth.authorize(params["code"])
        refresh_token_dict = {'token': refresh_token}
        send_message(
            client, f"<b> YOU CAN CLOSE THIS WINDOW</b> Refresh token: {refresh_token}")

        # write to file
        with open('token.json', 'w') as file:
            file.write(json.dumps(refresh_token_dict))
            file.close()
        with open('token.json', 'r') as file:
            token = json.loads(file.read())
        return token


def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client


def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()


if __name__ == "__main__":
    sys.exit(main())
