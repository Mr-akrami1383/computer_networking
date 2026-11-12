
import socket
import dns.resolver
import dns.exception

from dns.resolver import NXDOMAIN, NoAnswer, NoNameservers

from config_manager import load_config


# Load project configuration
config = load_config()

HOST = config["upstream_ip"]
PORT = config["upstream_port"]

request_count = 0


def real_dns_lookup(domain):
    """
    Resolve a domain using a real DNS server.
    """

    resolver = dns.resolver.Resolver(configure=False)

    resolver.nameservers = [config["dns_server_ip"]]

    try:
        answer = resolver.resolve(
            domain,
            "A",
            lifetime=config["upstream_timeout_sec"]
        )

        ip = str(answer[0].address)
        ttl = int(answer.rrset.ttl)

        return f"OK,{ip},{ttl}"

    except (NXDOMAIN, NoAnswer):
        return "ERROR,DOMAIN_NOT_FOUND"

    except (
        dns.exception.Timeout,
        NoNameservers,
        dns.exception.DNSException,
        OSError
    ):
        return "ERROR,SERVER_ERROR"


def simulated_dns_lookup(domain):
    """
    Return simulated DNS responses.
    """

    if domain == "missing.example.net":
        return "ERROR,DOMAIN_NOT_FOUND"

    ip = "198.51.100.7"
    ttl = 5

    return f"OK,{ip},{ttl}"


server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind((HOST, PORT))

print(f"Upstream server is running on {HOST}:{PORT}")

if config["real_dns_enabled"]:
    print("DNS Mode: REAL")
else:
    print("DNS Mode: SIMULATED")


while True:

    # Receive request from Proxy
    data, client_address = server.recvfrom(1024)

    try:
        domain = data.decode("utf-8").strip().lower()

    except UnicodeDecodeError:
        server.sendto(
            b"ERROR,SERVER_ERROR",
            client_address
        )
        continue

    request_count += 1

    print(f"Request #{request_count}: {domain}")
    if config["real_dns_enabled"]:

        response = real_dns_lookup(domain)

    else:

        response = simulated_dns_lookup(domain)

    server.sendto(
        response.encode("utf-8"),
        client_address
    )

    print(f"Response: {response}")
