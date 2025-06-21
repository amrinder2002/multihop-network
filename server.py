"""Simple threaded chat server used for the multi-hop network demo."""

from __future__ import annotations

import argparse
import logging
import random
import socket
import threading
from dataclasses import dataclass
from typing import Dict, Tuple

DISCOVERY_PORT = 5577
DISCOVERY_MSG = "DISCOVER_SERVER"
DISCOVERY_RESP = "SERVER_INFO"


FORMAT = "utf-8"
SIZE = 1024
DISCONNECT_MSG = "!DISCONNECT"
FORWARD_MSG = "!ADDRESS"
LIST_MSG = "!LIST"


@dataclass
class ClientInfo:
    name: str
    address: Tuple[str, int]
    connection: socket.socket
    pin: str
    port: int


class ChatServer:
    """Threaded chat server."""

    def __init__(self, host: str, port: int, disc_port: int = DISCOVERY_PORT) -> None:
        self.host = host
        self.port = port
        self.disc_port = disc_port
        self.addr = (host, port)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.addr)
        self.server.listen()
        # discovery socket for clients to auto-detect the server
        self.disc_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.disc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.disc_socket.bind(("", self.disc_port))
        threading.Thread(target=self._discovery_loop, daemon=True).start()
        self.clients: Dict[str, ClientInfo] = {}
        logging.info("Server listening on %s:%s", host, port)

    def _discovery_loop(self) -> None:
        """Respond to UDP discovery requests."""
        while True:
            try:
                msg, addr = self.disc_socket.recvfrom(SIZE)
            except OSError:
                break
            if msg.decode(FORMAT) == DISCOVERY_MSG:
                response = f"{DISCOVERY_RESP} {self.host} {self.port}".encode(
                    FORMAT
                )
                self.disc_socket.sendto(response, addr)

    def broadcast(self) -> None:
        """Send the list of connected clients to everyone."""
        names = list(self.clients.keys())
        ports = [info.port for info in self.clients.values()]
        for info in self.clients.values():
            info.connection.send(f"[LIST] CONNECTION LIST: {names}".encode(FORMAT))
            info.connection.send(
                f"[LIST] CONNECTION LIST: {ports}".encode(FORMAT)
            )

    def handle_client(self, conn: socket.socket, addr: Tuple[str, int], name: str) -> None:
        """Handle messages from a connected client."""
        logging.info("New connection %s:%s as %s", addr[0], addr[1], name)
        connected = True
        while connected:
            msg = conn.recv(SIZE).decode(FORMAT)
            if msg == DISCONNECT_MSG:
                logging.info("%s disconnected", name)
                conn.send(DISCONNECT_MSG.encode(FORMAT))
                conn.close()
                connected = False
                break

            if msg == FORWARD_MSG:
                conn.send("!USERNAME".encode(FORMAT))
                target = conn.recv(SIZE).decode(FORMAT)
                if target in self.clients:
                    t_info = self.clients[target]
                    conn.send(t_info.address[0].encode(FORMAT))
                    conn.send(str(t_info.port).encode(FORMAT))
                continue

            if msg == LIST_MSG:
                conn.send(str(list(self.clients.keys())).encode(FORMAT))
                continue

            logging.info("[%s:%s] %s", name, addr, msg)
            conn.send(f"Msg received: {msg}".encode(FORMAT))

    def run(self) -> None:
        """Run the server loop accepting clients."""
        temp_port = self.port + 1
        while True:
            conn, addr = self.server.accept()

            # username negotiation
            while True:
                temp_name = conn.recv(SIZE).decode(FORMAT)
                if temp_name in self.clients:
                    conn.send("!NOTACCEPTED".encode(FORMAT))
                else:
                    conn.send(temp_name.encode(FORMAT))
                    break

            temp_pin = str(random.randint(1000, 9999))
            logging.info("Authenticating %s with pin %s", temp_name, temp_pin)
            msg_pin = conn.recv(SIZE).decode(FORMAT)
            if msg_pin != temp_pin:
                conn.send("!NOTACCEPTED".encode(FORMAT))
                conn.close()
                continue

            conn.send("!ACCEPTED".encode(FORMAT))
            conn.recv(SIZE)
            conn.send(str(temp_port).encode(FORMAT))

            info = ClientInfo(
                name=temp_name,
                address=addr,
                connection=conn,
                pin=temp_pin,
                port=temp_port,
            )
            self.clients[temp_name] = info
            temp_port += 1
            threading.Thread(
                target=self.handle_client, args=(conn, addr, temp_name), daemon=True
            ).start()
            self.broadcast()
            logging.info("Active connections: %s", len(self.clients))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chat server")
    parser.add_argument("--host", default=socket.gethostbyname(socket.gethostname()))
    parser.add_argument("--port", type=int, default=5566)
    parser.add_argument("--disc-port", type=int, default=DISCOVERY_PORT, help="UDP discovery port")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    args = parse_args()
    server = ChatServer(args.host, args.port, args.disc_port)
    server.run()


if __name__ == "__main__":
    main()
