import ipaddress
import socket
from urllib.parse import urlparse
from app.core.exceptions import SSRFSecurityViolation

DISALLOWED_SCHEMES = {"file", "gopher", "ftp", "smtp", "ldap", "dict"}

def is_ip_private_or_restricted(ip_str: str) -> bool:
    """Checks if an IP address is private, loopback, link-local, or cloud metadata."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
            # Cloud metadata service (169.254.169.254)
            or ip_str == "169.254.169.254"
        )
    except ValueError:
        return True

def validate_url_for_ssrf(url: str) -> None:
    """
    Validates a URL against SSRF vulnerabilities before fetching.
    Resolves hostname to IP and verifies IP against private/restricted ranges.
    """
    parsed = urlparse(url)

    if not parsed.scheme or parsed.scheme.lower() not in {"http", "https"}:
        raise SSRFSecurityViolation(url, f"Scheme '{parsed.scheme}' is not permitted. Only HTTP and HTTPS are allowed.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFSecurityViolation(url, "URL missing valid hostname.")

    # Deny direct localhost string names
    if hostname.lower() in {"localhost", "127.0.0.1", "0.0.0.0", "::1"}:
        raise SSRFSecurityViolation(url, "Targeting localhost or loopback is strictly prohibited.")

    # Resolve hostname via DNS
    try:
        # getaddrinfo returns list of (family, type, proto, canonname, sockaddr)
        addr_info = socket.getaddrinfo(hostname, None)
        resolved_ips = {item[4][0] for item in addr_info}
    except socket.gaierror as e:
        raise SSRFSecurityViolation(url, f"DNS resolution failed for hostname '{hostname}': {e}")

    for ip in resolved_ips:
        if is_ip_private_or_restricted(ip):
            raise SSRFSecurityViolation(
                url,
                f"Hostname '{hostname}' resolved to restricted IP address '{ip}' (private, loopback, or cloud metadata)."
            )
