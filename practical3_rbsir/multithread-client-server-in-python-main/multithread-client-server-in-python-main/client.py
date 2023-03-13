import socket
import threading
import time

c_obj = threading.Condition()
IP = socket.gethostbyname(socket.gethostname())
PORT = 5566
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"
KEYWORDS = ['!NOTACCEPTED', '!DISCONNECT', '!ACCEPTED', '!LIST', '!ADDRESS']
DISCONNECT_MSG = "!DISCONNECT"
USERNAME = None
PIN = None
client = None
s_client = None
S_PORT = None


def send_message():
    # c_obj.acquire()
    while True:
        msg = input("")

        globals()['client'].send(msg.encode(FORMAT))
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
        msg = globals()['client'].recv(SIZE).decode(FORMAT)
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
    ADDR2 = (IP, S_PORT)
    print("[S_CLIENT] SEVER_CLIENT is starting...")
    s_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_client.bind(ADDR2)
    s_client.listen()
    print(f"[S_CLIENT] S_CLIENT is listening on {IP}:{S_PORT}")

    while True:
        conn, addr = s_client.accept()
        temp_msg = conn.recv(SIZE).decode(FORMAT)
        print(f"[INTERUP CLIENT] {temp_msg}")
        conn.send("Msg Recieved".encode(FORMAT))
        conn.close()

    pass


def main():

    while True:
        print(f"[CONNECTING] Client connecting to server at {IP}:{PORT}")
        globals()['client'] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        globals()['client'].connect(ADDR)
        print(f"[CONNECTED] Client connected to server at {IP}:{PORT}")

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
            f"[AUTHENTICATED] credentials are verified by server at {IP}:{PORT}")

        print(f"[Waiting] Waiting for port number from {IP}:{PORT}")
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
