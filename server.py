import socket
import threading
import random
import time
# import wikipedia

IP = socket.gethostbyname(socket.gethostname())
# IP = "172.20.10.3"
PORT = 5566
# PORT = ""
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
DISCOVERY_PORT = 5570
DISCONNECT_MSG = "!DISCONNECT"
FORWARD_MSG = "!ADDRESS"
LIST_MSG = "!LIST"
v_name = []
v_addr = []
v_conn = []
v_pin = []
v_port = []

print(f"IP = {IP}\n")

print("[STARTING] Server is starting...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print(f"[LISTENING] Server is listening on {IP}:{PORT}")


def discovery_broadcast():
    """Broadcast server address for automatic discovery."""
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    msg = f"SERVE:{IP}:{PORT}".encode(FORMAT)
    while True:
        try:
            udp.sendto(msg, ("<broadcast>", DISCOVERY_PORT))
        except Exception:
            pass
        time.sleep(5)

def broadcast():
    i = 0
    for addr in v_conn:
        msg = str(v_name)
        msg = "[LIST] CONNECTION LIST: " + msg
        addr.send(msg.encode(FORMAT))
        msg = str(v_port)
        msg = "[LIST] CONNECTION LIST: " + msg
        addr.send(msg.encode(FORMAT))
        i = i+1
    pass


def handle_client(conn, addr, u_name):
    print(f"[SERVER] [NEW CONNECTION] {u_name}:{addr} connected.")

    connected = True
    while connected:
        msg = conn.recv(SIZE).decode(FORMAT)
        if msg == DISCONNECT_MSG:
            print(f"[SERVER][ACTIVE CONNECTIONS] {threading.active_count() - 2}")
            conn.send(DISCONNECT_MSG.encode(FORMAT))
            conn.close()
            connected = False
        if msg == FORWARD_MSG:
            conn.send("!USERNAME".encode(FORMAT))
            msg = conn.recv(SIZE).decode(FORMAT)
            i=0
            for name in v_name:
                print(f"{i} ")
                if msg == name:
                    break
                i+=1
            print(f"{i} ")
            
            t = v_addr[i]
            t_ip = str(t[0])
            t_port = str(v_port[i])

            conn.send(t_ip.encode(FORMAT))
            conn.send(t_port.encode(FORMAT))
            continue


        if msg == LIST_MSG:
            msg = f"Msg received: {msg}"
            msg = str(v_name)
            conn.send(msg.encode(FORMAT))
            continue


        print(f"[{u_name}:{addr}] {msg}")
        msg = f"Msg received: {msg}"
        # msg = wikipedia.summary(msg, sentences=1)
        conn.send(msg.encode(FORMAT))

    conn.close()


def main():
    temp_port = PORT+1
    threading.Thread(target=discovery_broadcast, daemon=True).start()
    while True:
        conn, addr = server.accept()
        while True:
            temp_name = conn.recv(SIZE).decode(FORMAT)
            print(f"[CLIENT] Username: {temp_name}")
            if temp_name in v_name:
                print("[SERVER] Username not accepted")
                conn.send("!NOTACCEPTED".encode(FORMAT))
            else:
                print("[SERVER] Username accepted")
                conn.send(temp_name.encode(FORMAT))
                break
        
        temp_pin = str(random.randint(1000, 9999))
        print(f"[AUTHENTICATING] Current Pin: {temp_pin}")
        msg_pin = conn.recv(SIZE).decode(FORMAT)
        
        if msg_pin != temp_pin:
            print("[SERVER] PIN not accepted")
            conn.send("!NOTACCEPTED".encode(FORMAT))
            conn.close()
            break
        else:
            print("[SERVER] PIN accepted")
            conn.send("!ACCEPTED".encode(FORMAT))
        
        
        conn.recv(SIZE).decode(FORMAT)
        conn.send(str(temp_port).encode(FORMAT))
        
        
        

        print(f"[SERVER] {temp_name} added to network")

        thread = threading.Thread(target=handle_client, args=(conn, addr, temp_name))
        thread.start()
        v_pin.append(temp_pin)
        v_name.append(temp_name)
        v_addr.append(addr)
        v_conn.append(conn)
        v_port.append(temp_port)
        temp_port += 1
        broadcast()
        print(f"\n[SERVER][ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        pass
    pass


if __name__ == "__main__":
    main()
