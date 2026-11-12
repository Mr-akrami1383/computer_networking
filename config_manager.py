
from pathlib import Path
import ipaddress


def load_config(filename="config.txt"):
    config = {}

    file_path = Path(filename)

    with file_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()


    config.setdefault("log_enabled", "false")
    config.setdefault("log_file", "log.txt")


    config.setdefault("real_dns_enabled", "false")
    config.setdefault("dns_server_ip", "8.8.8.8")

    required_keys = [
        "upstream_ip",
        "upstream_port",
        "upstream_timeout_sec",
        "sinkhole_ip",
        "proxy_ip",
        "local_ttl",
        "ad_list_file",
        "sanction_list_file",
        "cache_enabled",
    ]

    for key in required_keys:
        if key not in config or not config[key]:
            raise ValueError(f"Missing config value: {key}")

    try:
        config["upstream_port"] = int(config["upstream_port"])
        config["upstream_timeout_sec"] = float(
            config["upstream_timeout_sec"]
        )
        config["local_ttl"] = int(config["local_ttl"])

    except ValueError:
        raise ValueError("Invalid numeric value in config.txt")

    if not 1 <= config["upstream_port"] <= 65535:
        raise ValueError("Invalid upstream_port")

    if config["upstream_timeout_sec"] <= 0:
        raise ValueError("Invalid upstream_timeout_sec")

    if config["local_ttl"] < 0:
        raise ValueError("Invalid local_ttl")
    ip_keys = [
        "upstream_ip",
        "sinkhole_ip",
        "proxy_ip",
        "dns_server_ip",
    ]

    for key in ip_keys:
        try:
            ipaddress.IPv4Address(config[key])

        except ipaddress.AddressValueError:
            raise ValueError(f"Invalid IPv4 address: {key}")
    boolean_keys = [
        "cache_enabled",
        "log_enabled",
        "real_dns_enabled",
    ]

    for key in boolean_keys:
        value = config[key].lower()

        if value not in ("true", "false"):
            raise ValueError(f"Invalid boolean value: {key}")

        config[key] = value == "true"

    return config
