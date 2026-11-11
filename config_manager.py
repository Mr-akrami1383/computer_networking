from pathlib import Path


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

    config["upstream_port"] = int(config["upstream_port"])
    config["upstream_timeout_sec"] = int(config["upstream_timeout_sec"])
    config["local_ttl"] = int(config["local_ttl"])
    config["cache_enabled"] = config["cache_enabled"].lower() == "true"

    return config