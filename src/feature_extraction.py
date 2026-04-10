import re
from urllib.parse import urlparse

def extract_features(url):
    features = []

    parsed = urlparse(url)
    domain = parsed.netloc

    # 1. index (dummy)
    features.append(0)

    # 2. having_IP_Address
    ip_pattern = r'\d+\.\d+\.\d+\.\d+'
    features.append(1 if re.search(ip_pattern, url) else 0)

    # 3. URL_Length
    features.append(len(url))

    # 4. Shortening Service
    features.append(1 if "bit.ly" in url or "tinyurl" in url else 0)

    # 5. having @
    features.append(1 if "@" in url else 0)

    # 6. double slash
    features.append(1 if "//" in url[7:] else 0)

    # 7. prefix suffix (-)
    features.append(1 if "-" in domain else 0)

    # 8. subdomain
    features.append(domain.count("."))

    # 9. SSL final state
    features.append(1 if parsed.scheme == "https" else 0)

    # 10. domain registration length (dummy)
    features.append(0)

    # 11. favicon (dummy)
    features.append(0)

    # 12. port
    features.append(1 if ":" in domain else 0)

    # 13. HTTPS token
    features.append(1 if "https" in domain else 0)

    # 14–31 → remaining (dummy placeholders)
    for _ in range(31 - len(features)):
        features.append(0)

    return features