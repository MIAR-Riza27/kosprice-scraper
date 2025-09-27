import socket
from tools.config import SCRAPER_CONFIG


def check_internet(host="8.8.8.8", port=53, timeout=None):
    if timeout is None:
        timeout = SCRAPER_CONFIG.get("internet_check_timeout", 3)
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False
