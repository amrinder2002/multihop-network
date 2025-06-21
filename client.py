"""Command line chat client for the multi-hop network demo."""

from __future__ import annotations

import argparse
import logging
import socket
import threading
from typing import Tuple

DISCOVERY_PORT = 5577
DISCOVERY_MSG = "DISCOVER_SERVER"
DISCOVERY_RESP = "SERVER_INFO"

FORMAT = "utf-8"
SIZE = 1024
DISCONNECT_MSG = "!DISCONNECT"
FORWARD_MSG = "!ADDRESS"
LIST_MSG = "!LIST"


class ChatClient:
    def __init__(self, host: str | None, port: int, disc_port: int = DISCOVERY_PORT) -> None:
        self.host = host
        self.port = port
        self.disc_port = disc_port
        self.addr: Tuple[str, int] | None = (host, port) if host else None
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username: str | None = None
        self.pin: str | None = None
        self.s_port: int | None = None

    def discover_server(self, timeout: float = 3.0) -> Tuple[str, int]:
        """Broadcast a UDP packet to locate the server."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        try:
            sock.sendto(DISCOVERY_MSG.encode(FORMAT), ("255.255.255.255", self.disc_port))
            data, addr = sock.recvfrom(SIZE)
        except OSError as exc:
            raise RuntimeError("Server discovery failed") from exc
        finally:
            sock.close()
        parts = data.decode(FORMAT).split()
        if len(parts) == 3 and parts[0] == DISCOVERY_RESP:
            return parts[1], int(parts[2])
        raise RuntimeError("Invalid discovery response")

    def reconnect(self) -> None:
        """Re-establish connection to the server."""
        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = None
        self.connect()
        if self.username and self.pin:
            try:
                self.authenticate(self.username, self.pin)
            except Exception as exc:
                logging.error("Re-authentication failed: %s", exc)

    def connect(self) -> None:
        if self.addr is None:
            self.addr = self.discover_server()
        try:
            self.client.connect(self.addr)
        except OSError:
            # attempt discovery again on failure
            self.addr = self.discover_server()
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
        self.pin = pin
        logging.info("Authenticated. Assigned port %s", self.s_port)

    def send_loop(self) -> None:
        while True:
            msg = input()
            try:
                self.client.send(msg.encode(FORMAT))
            except OSError:
                logging.warning("Connection lost, attempting to reconnect...")
                self.reconnect()
                continue
            if msg == DISCONNECT_MSG:
                break

    def recv_loop(self) -> None:
        while True:
            try:
                msg = self.client.recv(SIZE).decode(FORMAT)
            except OSError:
                logging.warning("Connection lost, attempting to reconnect...")
                self.reconnect()
                continue
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
    parser.add_argument("--host", help="Server host; if omitted discovery is used", default=None)
    parser.add_argument("--port", type=int, default=5566)
    parser.add_argument("--disc-port", type=int, default=DISCOVERY_PORT, help="UDP discovery port")
    parser.add_argument("username", help="Username to use")
    parser.add_argument("pin", help="Authentication PIN")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    args = parse_args()
    client = ChatClient(args.host, args.port, args.disc_port)
    try:
        client.run(args.username, args.pin)
    except Exception as exc:
        logging.error("Error: %s", exc)


if __name__ == "__main__":
    main()
