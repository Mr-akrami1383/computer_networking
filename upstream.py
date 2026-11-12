
import socket

HOST = "127.0.0.1"
PORT = 5354

request_count = 0

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server.bind((HOST, PORT))

print(f"Upstream server is running on {HOST}:{PORT}")

while True:
    data, client_address = server.recvfrom(1024)
    domain = data.decode("utf-8").strip().lower()
    request_count += 1

    # Check domain
    if domain == "missing.example.net":

        response = "ERROR,DOMAIN_NOT_FOUND"
        print(f"Request #{request_count}: {domain} -> NOT_FOUND")

    else:

        ip = "198.51.100.7"
        ttl = 5

        response = f"OK,{ip},{ttl}"
        print(f"Request #{request_count}: {domain} -> OK {ip} {ttl}")
    server.sendto(response.encode("utf-8"), client_address)
