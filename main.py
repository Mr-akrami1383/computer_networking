
from config_manager import load_config
from lists_manager import load_lists
from domain_handler import normalize_domain, classify_domain
from upstream_client import query_upstream
from logging_manager import log_result
from cache_manager import CacheManager


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

        raw_cache = config.get("cache_enabled", True)
        cache_enabled = (
            str(raw_cache).lower() == "true" if not isinstance(raw_cache, bool) else raw_cache
        )
        max_entries_raw = config.get("cache_max_entries")
        max_entries = int(max_entries_raw) if max_entries_raw is not None else None

        cache_mgr = CacheManager(cache_enabled=cache_enabled, max_entries=max_entries)

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

        if command == "stats":
            print(cache_mgr.format_stats())
            continue

        if command == "cache":
            print(cache_mgr.format_cache_contents())
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
            cached_result = cache_mgr.get(domain)
            if cached_result is not None:
                source = "CACHE"
                ip, ttl = cached_result
                status = "OK"
            else:
                status, ip, ttl = query_upstream(domain, config)

                if status == "OK" and ttl > 0:
                    cache_mgr.put(domain, ip, ttl)

        cache_mgr.record_decision(source, status)

        print_result(domain, source, status, ip, ttl)
        log_result(domain, source, status, ip, ttl, config)


if __name__ == "__main__":
    main()
