
import socket

from config_manager import load_config


config = load_config()

HOST = config["upstream_ip"]
PORT = config["upstream_port"]

request_count = 0


def simulated_dns_lookup(domain):
    """
    پاسخ‌دهی شبیه‌سازی‌شده برای دامنه‌های آزمایشی پروژه.
    """

    if domain == "missing.example.net":
        return "ERROR,DOMAIN_NOT_FOUND"

    return "OK,198.51.100.7,5"


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print(f"Simulated Upstream is running on {HOST}:{PORT}")


while True:
    data, client_address = server.recvfrom(1024)

    try:
        domain = data.decode("utf-8").strip().lower()

        request_count += 1
        print(f"Request #{request_count}: {domain}")

        response = simulated_dns_lookup(domain)

    except (UnicodeDecodeError, Exception):
        response = "ERROR,SERVER_ERROR"

    server.sendto(response.encode("utf-8"), client_address)

    print(f"Response: {response}")
