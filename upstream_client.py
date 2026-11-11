
import socket
import ipaddress


def query_upstream(domain, config):
    address = (config["upstream_ip"], config["upstream_port"])

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.settimeout(config["upstream_timeout_sec"])
            client.sendto(domain.encode("utf-8"), address)

            response, _ = client.recvfrom(1024)

        response = response.decode("utf-8").strip()
        parts = response.split(",")

        if len(parts) == 3 and parts[0] == "OK":
            try:
                ip = str(ipaddress.IPv4Address(parts[1]))
                ttl = int(parts[2])
            except ValueError:
                return "SERVER_ERROR", "-", "-"

            if ttl < 0:
                return "SERVER_ERROR", "-", "-"

            return "OK", ip, ttl

        if len(parts) == 2 and parts[0] == "ERROR":
            if parts[1] == "DOMAIN_NOT_FOUND":
                return "NOT_FOUND", "-", "-"

        return "SERVER_ERROR", "-", "-"

    except (socket.timeout, OSError, UnicodeDecodeError):
        return "SERVER_ERROR", "-", "-"
