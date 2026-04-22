import re
from urllib.parse import urlparse


SHORTENER_DOMAINS = {
    "bit.ly", "goo.gl", "tinyurl.com", "ow.ly", "t.co", "is.gd", "buff.ly",
    "adf.ly", "rebrand.ly", "cutt.ly", "shorturl.at"
}


def _get_domain(parsed_url):
    return parsed_url.netloc.split("@")[ -1 ].split(":")[0].lower()


def _has_ipv4(domain):
    return bool(re.fullmatch(r"\d+\.\d+\.\d+\.\d+", domain))


def _subdomain_score(domain):
    dot_count = domain.count(".")
    if dot_count <= 1:
        return 1
    if dot_count == 2:
        return 0
    return -1


def extract_features(url):
    """
    Builds 31 model features in the same order as cleaned_data.csv (excluding label).
    Many original dataset features are page-content based; these are set to neutral (0)
    when they cannot be inferred from the URL string alone.
    """
    parsed = urlparse(url.strip())
    domain = _get_domain(parsed)
    full_url = url.strip().lower()

    features = []

    # 1) index
    features.append(0)

    # 2) having_IPhaving_IP_Address
    features.append(-1 if _has_ipv4(domain) else 1)

    # 3) URLURL_Length
    url_len = len(full_url)
    if url_len < 54:
        features.append(1)
    elif url_len <= 75:
        features.append(0)
    else:
        features.append(-1)

    # 4) Shortining_Service
    features.append(-1 if domain in SHORTENER_DOMAINS else 1)

    # 5) having_At_Symbol
    features.append(-1 if "@" in full_url else 1)

    # 6) double_slash_redirecting
    features.append(-1 if "//" in full_url[8:] else 1)

    # 7) Prefix_Suffix
    features.append(-1 if "-" in domain else 1)

    # 8) having_Sub_Domain
    features.append(_subdomain_score(domain))

    # 9) SSLfinal_State
    features.append(1 if parsed.scheme == "https" else -1)

    # 10) Domain_registeration_length (cannot infer from URL only)
    features.append(0)

    # 11) Favicon (cannot infer from URL only)
    features.append(0)

    # 12) port
    if parsed.port is None or parsed.port in (80, 443):
        features.append(1)
    else:
        features.append(-1)

    # 13) HTTPS_token
    features.append(-1 if "https" in domain else 1)

    # 14) Request_URL (cannot infer without page fetch)
    features.append(0)

    # 15) URL_of_Anchor (cannot infer without page fetch)
    features.append(0)

    # 16) Links_in_tags (cannot infer without page fetch)
    features.append(0)

    # 17) SFH (cannot infer without page fetch)
    features.append(0)

    # 18) Submitting_to_email
    features.append(-1 if "mailto:" in full_url else 1)

    # 19) Abnormal_URL
    features.append(1 if domain and domain in full_url else -1)

    # 20) Redirect
    redirect_markers = full_url.count("//")
    if redirect_markers > 2:
        features.append(-1)
    elif redirect_markers == 2:
        features.append(0)
    else:
        features.append(1)

    # 21-24) on_mouseover, RightClick, popUpWidnow, Iframe
    features.extend([0, 0, 0, 0])

    # 25-31) age_of_domain, DNSRecord, web_traffic, Page_Rank,
    #        Google_Index, Links_pointing_to_page, Statistical_report
    features.extend([0, 0, 0, 0, 0, 0, 0])

    return features