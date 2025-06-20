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

Both programs accept `--host` and `--port` options so the network settings can
be customised.  The client requires a username and a pin for authentication.
