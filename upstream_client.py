import socket
import ipaddress

TEST_DOMAINS = (
    "example.com",
    "example.net",
    "example.org"
)


def is_test_domain(domain):
    """
    بررسی می‌کند دامنه متعلق به دامنه‌های آزمایشی پروژه است یا نه.
    """
    return any(
        domain == test_domain or domain.endswith("." + test_domain)
        for test_domain in TEST_DOMAINS
    )


def query_simulated_dns(domain, config):
    """
    ارسال درخواست متنی UDP به شبیه‌ساز محلی پروژه.
    """

    address = (
        config["upstream_ip"],
        config["upstream_port"]
    )

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.settimeout(config["upstream_timeout_sec"])

            client.sendto(domain.encode("utf-8"), address)

            response, _ = client.recvfrom(1024)

        response = response.decode("utf-8").strip()
        parts = response.split(",")

        if len(parts) == 3 and parts[0] == "OK":
            ip = str(ipaddress.IPv4Address(parts[1]))
            ttl = int(parts[2])

            if ttl < 0:
                return "SERVER_ERROR", "-", "-"

            return "OK", ip, ttl

        if len(parts) == 2 and parts[0] == "ERROR":
            if parts[1] == "DOMAIN_NOT_FOUND":
                return "NOT_FOUND", "-", "-"

        return "SERVER_ERROR", "-", "-"

    except (
        socket.timeout,
        OSError,
        UnicodeDecodeError,
        ValueError
    ):
        return "SERVER_ERROR", "-", "-"


def query_real_dns(domain, config):
    """
    استعلام واقعی DNS برای دامنه‌های عادی اینترنت.
    """

    try:
        import dns.resolver
        import dns.exception

        resolver = dns.resolver.Resolver(configure=False)

        resolver.nameservers = [
            config.get("dns_server_ip", "8.8.8.8")
        ]

        resolver.port = 53
        resolver.timeout = config["upstream_timeout_sec"]

        answer = resolver.resolve(
            domain,
            "A",
            lifetime=config["upstream_timeout_sec"],
            search=False
        )

        if answer.rrset is None or len(answer) == 0:
            return "NOT_FOUND", "-", "-"

        ip = str(ipaddress.IPv4Address(answer[0].address))
        ttl = int(answer.rrset.ttl)

        if ttl < 0:
            return "SERVER_ERROR", "-", "-"

        return "OK", ip, ttl

    except ImportError:
        return "SERVER_ERROR", "-", "-"

    except dns.resolver.NXDOMAIN:
        return "NOT_FOUND", "-", "-"

    except dns.resolver.NoAnswer:
        return "NOT_FOUND", "-", "-"

    except (
        dns.resolver.NoNameservers,
        dns.exception.Timeout,
        dns.exception.DNSException,
        OSError,
        ValueError
    ):
        return "SERVER_ERROR", "-", "-"


def query_upstream(domain, config):
    """
    انتخاب خودکار مسیر درخواست بر اساس نام دامنه.
    """

    if is_test_domain(domain):
        return query_simulated_dns(domain, config)

    return query_real_dns(domain, config)