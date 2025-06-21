import socket
import threading
import time

c_obj = threading.Condition()
LOCAL_IP = socket.gethostbyname(socket.gethostname())
SERVER_IP = None
PORT = 5566
DISCOVERY_PORT = 5570
ADDR = None
SIZE = 1024
FORMAT = "utf-8"
KEYWORDS = ['!NOTACCEPTED', '!DISCONNECT', '!ACCEPTED', '!LIST', '!ADDRESS']
DISCONNECT_MSG = "!DISCONNECT"
USERNAME = None
PIN = None
client = None
s_client = None
S_PORT = None
reconnect_lock = threading.Lock()


def discover_server():
    """Listen for server broadcast and return its address."""
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp.bind(("", DISCOVERY_PORT))
    while True:
        data, _ = udp.recvfrom(SIZE)
        msg = data.decode(FORMAT)
        if msg.startswith("SERVE:"):
            _, ip, port = msg.split(":")
            return ip, int(port)


def connect_server():
    """Discover and connect to the server with retries."""
    global SERVER_IP, ADDR, client
    with reconnect_lock:
        while True:
            SERVER_IP, p = discover_server()
            ADDR = (SERVER_IP, p)
            print(f"[CONNECTING] Client connecting to server at {SERVER_IP}:{p}")
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(ADDR)
                print(f"[CONNECTED] Client connected to server at {SERVER_IP}:{p}")
                return
            except Exception:
                print("[RETRY] Connection failed. Searching again...")
                time.sleep(2)


def send_message():
    # c_obj.acquire()
    while True:
        msg = input("")
        try:
            globals()['client'].send(msg.encode(FORMAT))
        except Exception:
            print("[ERROR] Lost connection. Reconnecting...")
            connect_server()
            continue
        if msg == "!disconnect":
            exit()
        if msg == "!ADDRESS":
            time.sleep(1)
        #    c_obj.wait
        pass
        if msg == "!DISCONNECT":
            break
        pass
    # c_obj.release()


def recieve_messsage():
    # c_obj.acquire()
    while True:
        try:
            msg = globals()['client'].recv(SIZE).decode(FORMAT)
            if not msg:
                raise ConnectionError
        except Exception:
            print("[ERROR] Connection lost. Reconnecting...")
            connect_server()
            continue
        if msg == "!disconnect":
            exit()
        if msg == "!USERNAME":
            msg = input("[SERVER] To?: ")
            globals()['client'].send(msg.encode(FORMAT))
            t_ip = globals()['client'].recv(SIZE).decode(FORMAT)
            t_port = int(globals()['client'].recv(SIZE).decode(FORMAT))
            print(
                f"[CLIENT] t_ip: {t_ip} and t_port: {t_port}\n[CLIENT] 'PRESS ENTER'")
            T_ADDR = (t_ip, int(t_port))
            t_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            t_client.connect(T_ADDR)
            msg = input("INPUT INTERUPT MSG:> ")
            t_client.send(msg.encode(FORMAT))
            msg = t_client.recv(SIZE).decode(FORMAT)
            print("[INTERUPTED NODE] {msg}")
            # c_obj.notify()
            pass
        print(f"[SERVER] {msg}")
        pass
    # c_obj.release()


def run_s_client():
    ADDR2 = (LOCAL_IP, S_PORT)
    print("[S_CLIENT] SEVER_CLIENT is starting...")
    s_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_client.bind(ADDR2)
    s_client.listen()
    print(f"[S_CLIENT] S_CLIENT is listening on {LOCAL_IP}:{S_PORT}")

    while True:
        conn, addr = s_client.accept()
        temp_msg = conn.recv(SIZE).decode(FORMAT)
        print(f"[INTERUP CLIENT] {temp_msg}")
        conn.send("Msg Recieved".encode(FORMAT))
        conn.close()

    pass


def main():

    connect_server()

    while True:

    # [TAB] for inputting, sending and verifyin username
        if globals()['USERNAME'] == None or globals()['USERNAME'] == "!NOTACCEPTED":
            while True:
                globals()['USERNAME'] = input("[LOGIN] INPUT USERNAME: ")

                if globals()['USERNAME'] in KEYWORDS:
                    print("[KEYWORD ERROR] This name is reserved")
                    continue
                globals()['client'].send(globals()['USERNAME'].encode(FORMAT))
                temp_msg = globals()['client'].recv(SIZE).decode(FORMAT)
                if (temp_msg == globals()['USERNAME']):
                    print(f"[SERVER] Username accepted")
                    break
                else:
                    print("[NAME ERROR] Try another username")
                    continue

        if globals()['PIN'] == None:
            globals()['PIN'] = input("[LOGIN] Input PIN: ")
        globals()['client'].send(globals()['PIN'].encode(FORMAT))

        temp_msg = globals()['client'].recv(SIZE).decode(FORMAT)
        print(f"[SERVER] {temp_msg}")
        if temp_msg == "!NOTACCEPTED":
            break

        print(
            f"[AUTHENTICATED] credentials are verified by server at {SERVER_IP}:{PORT}")

        print(f"[Waiting] Waiting for port number from {SERVER_IP}:{PORT}")
        globals()['client'].send("PORT".encode(FORMAT))
        temp_msg = globals()['client'].recv(SIZE).decode(FORMAT)
        globals()['S_PORT'] = int(temp_msg)
        print(f"[SERVER] Your port number is {globals()['S_PORT']}")
        # input("end")
        break

    thread_recv = threading.Thread(target=recieve_messsage, args=())
    thread_recv.start()
    time.sleep(0.1)
    thread_s_client = threading.Thread(target=run_s_client, args=())
    thread_s_client.start()
    time.sleep(0.1)
    thread_send = threading.Thread(target=send_message, args=())
    thread_send.start()

    pass


if __name__ == "__main__":
    main()
