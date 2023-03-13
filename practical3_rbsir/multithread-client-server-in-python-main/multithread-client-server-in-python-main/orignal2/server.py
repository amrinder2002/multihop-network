import socket
import threading
import random
# import wikipedia

IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCONNECT_MSG = "!DISCONNECT"
vname = []
vip = []


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} of name {vname[-1]} is connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MSG:
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}")
            connected = False

        print(f"[{addr}] {msg}")
        msg = f"Msg received: {msg}"
        conn.send(msg.encode(FORMAT))

    conn.close()

def broadcast_list():
    pass


def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print(f"[LISTENING] Server is listening on {IP}:{PORT}")

    while True:

        conn, addr = server.accept()
        temp_name = conn.recv(SIZE).decode(FORMAT)
        if temp_name in vname:
            conn.send("NAME ALREADY OCCUPIED".encode(FORMAT))
            continue

        conn.send("ACCEPTED".encode(FORMAT))
        
        pin = random.randint(1000,9999)
        print(f"CURRENT PIN is: {pin}")

        temp_pin = conn.recv(SIZE).decode(FORMAT)
        if temp_pin == pin:
            conn.send("WRONG PIN".encode(FORMAT))
            continue
        
        vname.append(temp_name)
        vip.append(addr)
        print(vname)
        

        conn.send("ACCEPTED".encode(FORMAT))
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"\n[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    main()