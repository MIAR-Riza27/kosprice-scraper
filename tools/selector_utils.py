"""Utility functions for handling dynamic selectors"""

def detect_room_card_selector(page, selectors, timeout=10000):
    """
    Deteksi selector room card yang tepat untuk region ini.
    Coba primary dulu, kalau gagal coba fallback.
    
    Returns:
        str: Selector yang berhasil ditemukan
        None: Jika semua selector gagal
    """
    # Coba selector utama dulu
    try:
        page.wait_for_selector(
            selectors["room_card_primary"],
            timeout=timeout,
            state="attached"
        )
        print(f"    * [Using primary selector: {selectors['room_card_primary']}]")
        return selectors["room_card_primary"]
    except Exception:
        print(f"    X [Primary selector failed: {selectors['room_card_primary']}]")
    
    # Jika gagal, coba fallback
    try:
        page.wait_for_selector(
            selectors["room_card_fallback"],
            timeout=timeout,
            state="attached"
        )
        print(f"    ✓ [Using fallback selector: {selectors['room_card_fallback']}]")
        return selectors["room_card_fallback"]
    except Exception:
        print(f"    X [Fallback selector failed: {selectors['room_card_fallback']}]")
    
    # Semua gagal
    return None

def get_room_cards(page, selector):
    """
    Ambil semua room cards menggunakan selector yang sudah terdeteksi.
    
    Args:
        page: Playwright page object
        selector: CSS selector yang sudah terdeteksi
    
    Returns:
        list: List of card elements
    """
    return page.locator(selector).all()