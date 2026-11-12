"""Local UDP upstream simulator for the DNS Proxy assignment.

Run with: python upstream.py
No third-party dependencies are required.
"""

import socket


HOST = "127.0.0.1"
PORT = 5354  # The assignment allows a fixed port for this simulator.
BUFFER_SIZE = 65535


def make_reply(domain: str) -> str:
    if domain == "missing.example.net":
        return "NOT_FOUND"
    return "OK 198.51.100.7 5"


def main() -> None:
    request_count = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        try:
            server.bind((HOST, PORT))
        except OSError as exc:
            print(f"Upstream error: cannot bind to {HOST}:{PORT}: {exc}")
            return

        try:
            while True:
                data, client_address = server.recvfrom(BUFFER_SIZE)
                request_count += 1

                try:
                    message = data.decode("utf-8").strip()
                    parts = message.split()
                    if len(parts) != 2 or parts[0] != "QUERY":
                        raise ValueError("Expected QUERY <domain>")
                    domain = parts[1]
                    reply = make_reply(domain)
                except (UnicodeDecodeError, ValueError):
                    domain = "(invalid request)"
                    reply = "ERROR"

                print(
                    f"Request #{request_count}: {domain} -> {reply}",
                    flush=True,
                )

                try:
                    server.sendto(reply.encode("utf-8"), client_address)
                except OSError as exc:
                    print(f"Upstream error: cannot send reply: {exc}")
        except KeyboardInterrupt:
            pass
        except OSError as exc:
            print(f"Upstream error: {exc}")


if __name__ == "__main__":
    main()
"""Local UDP upstream simulator for the DNS Proxy assignment.

Run with: python upstream.py
No third-party dependencies are required.
"""

import socket


HOST = "127.0.0.1"
PORT = 5354  # The assignment allows a fixed port for this simulator.
BUFFER_SIZE = 65535


def make_reply(domain: str) -> str:
    """Return the deterministic response required by the assignment."""
    if domain == "missing.example.net":
        return "NOT_FOUND"
    return "OK 198.51.100.7 5"


def main() -> None:
    request_count = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        try:
            server.bind((HOST, PORT))
        except OSError as exc:
            print(f"Upstream error: cannot bind to {HOST}:{PORT}: {exc}")
            return

        try:
            while True:
                data, client_address = server.recvfrom(BUFFER_SIZE)
                request_count += 1

                try:
                    message = data.decode("utf-8").strip()
                    parts = message.split()
                    if len(parts) != 2 or parts[0] != "QUERY":
                        raise ValueError("Expected QUERY <domain>")
                    domain = parts[1]
                    reply = make_reply(domain)
                except (UnicodeDecodeError, ValueError):
                    domain = "(invalid request)"
                    reply = "ERROR"

                print(
                    f"Request #{request_count}: {domain} -> {reply}",
                    flush=True,
                )

                try:
                    server.sendto(reply.encode("utf-8"), client_address)
                except OSError as exc:
                    print(f"Upstream error: cannot send reply: {exc}")
        except KeyboardInterrupt:
            pass
        except OSError as exc:
            print(f"Upstream error: {exc}")


if __name__ == "__main__":
    main()
