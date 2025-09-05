"""Network utilities for connection checking and handling"""

import requests


def check_internet_connection(timeout: int = 5) -> bool:
    """Quick internet connection check"""
    try:
        response = requests.get("https://httpbin.org/get", timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


def check_connection_periodically(card_index: int, interval: int = 20) -> bool:
    """Check connection every N cards"""
    if card_index % interval == 0 and card_index > 0:
        return check_internet_connection()
    return True
