"""Configuration settings for the scraper"""

# Scraping settings
SCRAPER_CONFIG = {
    # --- URL & Template ---
    "base_url": "https://mamikos.com/cari",  # Base URL utama scraping
    "url_template": (
        "{base_url}/{region}/all/bulanan/0-15000000?keyword=&suggestion_type=search"
        "&rent=2&sort=price,-&price=10000-20000000&singgahsini=0"
    ),  # Template URL untuk setiap region

    # --- Timeout & Retry ---
    "page_timeout": 15000,  # Timeout saat buka halaman (ms)
    "load_timeout": 10000,  # Timeout tunggu elemen (ms)
    "max_connection_retry": 3,  # Maksimal percobaan cek koneksi internet sebelum scraper berhenti
    "internet_check_timeout": 3,  # Timeout cek koneksi internet (detik)
    "internet_retry_sleep": 10,  # Jeda antar percobaan koneksi (detik)
    "max_card_retry": 2,  # Jumlah maksimal percobaan ulang (retry) untuk card yang gagal

    # --- Scraping Logic ---
    "max_load_more_clicks": 30,  # Maksimal klik tombol 'load more' per region
    "scroll_pause": [
        1 / 3,
        2 / 3,
        1,
        0,
    ],  # Posisi scroll saat buka detail kos (relatif tinggi halaman)
    "completed_region_threshold": 150,  # Jika data region > ini, region dianggap sudah lengkap (skip)
    "duplicate_exit_threshold": 20,  # Maksimal duplikat sebelum region dihentikan

    # --- Backup & Data ---
    "backup_interval": 50,  # Backup otomatis setiap N card
}

# Browser settings
BROWSER_CONFIG = {
    "user_data_dir": r"C:\playwright",  # Folder data browser Playwright
    "channel": "chrome",  # Channel browser (chrome, msedge, dll)
    "headless": True,  # True = tanpa tampilan GUI
    "no_viewport": True,  # True = viewport default browser
}

# File paths
PATHS = {
    "data_dir": "backend/scraper/data",  # Folder utama data
    "backup_folder": "backend/scraper/data/backup",  # Folder backup otomatis
    "regions_folder": "backend/scraper/data/regions",  # Folder data per region
    "master_file": "data-scraper.json",  # Nama file data utama
    "failed_cards_folder": "backend/scraper/data/failed",  # Folder untuk simpan card gagal setelah retry
}

# CSS Selectors
SELECTORS = {
    "load_more_link": "a.list__content-load-link",
    "room_card": 'div[data-testid="roomCard"]',
    "room_name": ".detail-title__room-name",
    "gender": ".detail-kost-overview__gender-box",
    "area": ".detail-kost-overview__area-text",
    "rating": ".detail-kost-overview__rating-text",
    "review_count": ".detail-kost-overview__rating-review",
    "transaction_count": ".detail-kost-overview__total-transaction-text",
    "price": ".rc-price__text",
    "period": ".rc-price__type",
    "address": "#detailKostLocation p.bg-c-text--body-4",
    "facilities": ".detail-kost-facility-item__label",
    "rules": ".detail-kost-rule-item__label",
    "landmark_names": ".landmark-item__text-ellipsis",
    "landmark_distances": ".landmark-item__landmark-distance",
}
