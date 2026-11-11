from pathlib import Path
from domain_handler import normalize_domain

def load_domain_list(filename):
    domains = set()
    file_path = Path(filename)

    with file_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            domain = line.strip()

            if not domain or domain.startswith("#"):
                continue

            try:
                domain = normalize_domain(domain)
                domains.add(domain)
            except ValueError:
                print(f"Warning: bad line in {filename}: {line_number}")

    return domains

def load_lists(config):
    ad_domains = load_domain_list(config["ad_list_file"])
    sanction_domains = load_domain_list(config["sanction_list_file"])

    return ad_domains, sanction_domains