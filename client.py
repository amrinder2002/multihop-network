"""Command line chat client for the multi-hop network demo."""

from __future__ import annotations

import argparse
import logging
import socket
import threading
from typing import Tuple

FORMAT = "utf-8"
SIZE = 1024
DISCONNECT_MSG = "!DISCONNECT"
FORWARD_MSG = "!ADDRESS"
LIST_MSG = "!LIST"


class ChatClient:
    def __init__(self, host: str, port: int) -> None:
        self.addr = (host, port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username: str | None = None
        self.s_port: int | None = None

    def connect(self) -> None:
        self.client.connect(self.addr)
        logging.info("Connected to server at %s:%s", *self.addr)

    def authenticate(self, username: str, pin: str) -> None:
        self.client.send(username.encode(FORMAT))
        resp = self.client.recv(SIZE).decode(FORMAT)
        if resp != username:
            raise ValueError("Username not accepted")

        self.client.send(pin.encode(FORMAT))
        resp = self.client.recv(SIZE).decode(FORMAT)
        if resp != "!ACCEPTED":
            raise ValueError("PIN not accepted")

        self.client.send("PORT".encode(FORMAT))
        self.s_port = int(self.client.recv(SIZE).decode(FORMAT))
        self.username = username
        logging.info("Authenticated. Assigned port %s", self.s_port)

    def send_loop(self) -> None:
        while True:
            msg = input()
            self.client.send(msg.encode(FORMAT))
            if msg == DISCONNECT_MSG:
                break

    def recv_loop(self) -> None:
        while True:
            msg = self.client.recv(SIZE).decode(FORMAT)
            print(f"[SERVER] {msg}")
            if msg == DISCONNECT_MSG:
                break

    def run(self, username: str, pin: str) -> None:
        self.connect()
        self.authenticate(username, pin)

        recv_thread = threading.Thread(target=self.recv_loop, daemon=True)
        recv_thread.start()
        self.send_loop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Chat client")
    parser.add_argument("--host", default=socket.gethostbyname(socket.gethostname()))
    parser.add_argument("--port", type=int, default=5566)
    parser.add_argument("username", help="Username to use")
    parser.add_argument("pin", help="Authentication PIN")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    args = parse_args()
    client = ChatClient(args.host, args.port)
    try:
        client.run(args.username, args.pin)
    except Exception as exc:
        logging.error("Error: %s", exc)


if __name__ == "__main__":
    main()
