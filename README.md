# MultiHop Network

This repository contains Python networking examples including a multi-hop
file transfer and a threaded chat implementation.  The original scripts have
been refactored for clarity and now provide simple command line interfaces.

## Running the examples

### Server

```bash
python server.py --host 0.0.0.0 --port 5566
```

### Client

```bash
python client.py --host <server-ip> --port 5566 <username> <pin>
```

If `--host` is omitted, the client automatically discovers the server using a
UDP broadcast. Discovery uses port `5577` by default and can be customised with
`--disc-port`.

The client also attempts to reconnect automatically if the connection is
interrupted.

Both programs accept `--host` and `--port` options so the network settings can
be customised. The client requires a username and a PIN for authentication.
