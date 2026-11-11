
from config_manager import load_config
from lists_manager import load_lists
from domain_handler import normalize_domain, classify_domain
from upstream_client import query_upstream
from logging_manager import log_result


def print_result(domain, source, status, ip, ttl):
    print(f"Domain : {domain}")
    print(f"Source : {source}")
    print(f"Status : {status}")
    print(f"IP : {ip}")
    print(f"TTL : {ttl}")
    print()


def main():
    try:
        config = load_config()
        ad_domains, sanction_domains = load_lists(config)

    except (OSError, ValueError) as error:
        print(f"Config error: {error}")
        return

    print("DNS Proxy ready.")

    while True:
        raw_domain = input("Enter domain (or exit): ")
        command = raw_domain.strip().lower()

        if command == "exit":
            print("Bye.")
            break

        if command == "reload":
            try:
                ad_domains, sanction_domains = load_lists(config)
                print("Lists reloaded.")
            except OSError as error:
                print(f"Config error: {error}")
                break

            continue

        try:
            domain = normalize_domain(raw_domain)
        except ValueError:
            print_result(raw_domain, "NONE", "INVALID_INPUT", "-", "-")
            log_result(
                raw_domain, "NONE", "INVALID_INPUT", "-", "-", config
            )
            continue

        source = classify_domain(domain, ad_domains, sanction_domains)

        if source == "AD_BLOCK":
            ip = config["sinkhole_ip"]
            ttl = config["local_ttl"]
            status = "OK"

        elif source == "SANCTION":
            ip = config["proxy_ip"]
            ttl = config["local_ttl"]
            status = "OK"

        else:
            status, ip, ttl = query_upstream(domain, config)

        print_result(domain, source, status, ip, ttl)
        log_result(domain, source, status, ip, ttl, config)


if __name__ == "__main__":
    main()
