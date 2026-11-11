from datetime import datetime


def log_result(domain, source, status, ip, ttl, config):
    if not config["log_enabled"]:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"{timestamp} | {domain} | {source} | {status} | {ip} | {ttl}\n"

    with open(config["log_file"], "a", encoding="utf-8") as file:
        file.write(log_line)