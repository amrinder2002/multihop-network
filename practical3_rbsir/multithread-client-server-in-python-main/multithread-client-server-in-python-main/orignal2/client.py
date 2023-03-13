import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
PORT2 = 5500
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"


def listen():
    S_ADDR = (IP, PORT2)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(S_ADDR)
    client.listen()
    conn, addr = client.accept()
    print(f"[LISTENING] client is listening on {IP}:{PORT2}")
    print(f"[OTHERS] {client.recv(SIZE).decode(FORMAT)}")


def main():
    thread = threading.Thread(target=listen)
    thread.start()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

    while 1:
        msg = input("Enter username: ")
        client.send(msg.encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER] {msg}")

        if msg != "ACCEPTED":
            continue

        msg = input("Enter PIN: ")
        client.send(msg.encode(FORMAT))
        msg = client.recv(SIZE).decode(FORMAT)
        print(f"[SERVER] {msg}")
        
        if msg == "ACCEPTED":
            break


    connected = True
    while connected:
        msg = input("> ")

        client.send(msg.encode(FORMAT))

        if msg == DISCONNECT_MSG:
            connected = False
        else:
            msg = client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")


if __name__ == "__main__":
    main()
