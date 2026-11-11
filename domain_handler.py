import re


def normalize_domain(domain):
    if not isinstance(domain, str):
        raise ValueError("Invalid domain")

    domain = domain.strip().lower()

    if domain.endswith("."):
        domain = domain[:-1]

    if not domain:
        raise ValueError("Invalid domain")

    if len(domain) > 253:
        raise ValueError("Invalid domain")

    labels = domain.split(".")

    for label in labels:
        if not label or len(label) > 63:
            raise ValueError("Invalid domain")

        if not re.fullmatch(r"[a-z0-9-]+", label):
            raise ValueError("Invalid domain")

        if label.startswith("-") or label.endswith("-"):
            raise ValueError("Invalid domain")

    return domain


def domain_matches(domain, listed_domain):
    return domain == listed_domain or domain.endswith("." + listed_domain)


def classify_domain(domain, ad_domains, sanction_domains):
    for listed_domain in ad_domains:
        if domain_matches(domain, listed_domain):
            return "AD_BLOCK"

    for listed_domain in sanction_domains:
        if domain_matches(domain, listed_domain):
            return "SANCTION"

    return "UPSTREAM"