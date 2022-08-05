import socket
import threading
import random


# once two clients have been found, a game will begin
def game(client1, client2):
    # randomly selects which client goes first (red)
    # red player to go will always be referred to as "client1"
    if random.randint(0, 1) == 1:
        client1, client2 = client2, client1
    client1.send("red".encode())
    client2.send("blue".encode())

    # sends the red player a message to begin playing, and begins the game loop
    client1.send("play".encode())
    while True:
        # red's turn :
        move = -1
        client2.send("wait".encode())
        while True:
            move = int(client1.recv(1024).decode())
            if move != -1:
                client2.send(str(move).encode())
                print("CLIENT 1 PLAYED", move)
                break

        # blue's turn :
        move = -1
        client1.send("wait".encode())
        while True:
            move = int(client2.recv(1024).decode())
            if move != -1:
                client1.send(str(move).encode())
                print("CLIENT 2 PLAYED", move)
                break


def main():
    # socket setup
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 54321))
    server_socket.listen()

    # thread variables
    main_thread = []
    last_client = None

    # look for clients
    while True:
        client_socket, client_address = server_socket.accept()
        msg = client_socket.recv(1024)
        print(msg.decode())
        if msg.decode() == "CONNECT":
            print("CLIENT CONNECTED")
            client_socket.send("SEARCHING FOR GAME".encode())
            # add client to thread
            if last_client:
                t = threading.Thread(target=game, args=(last_client, client_socket))
                main_thread.append(t)
                t.start()
                last_client = None
            else:
                last_client = client_socket


if __name__ == "__main__":
    main()
