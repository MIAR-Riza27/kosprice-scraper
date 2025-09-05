"""Configuration settings for the scraper"""

# Scraping settings
SCRAPER_CONFIG = {
    "base_url": "https://mamikos.com/cari",
    "url_template": "{base_url}/{region}/all/bulanan/0-15000000?keyword={keyword}&suggestion_type=search&rent=2&sort=price,-&price=10000-20000000&singgahsini=0",
    "page_timeout": 15000,
    "load_timeout": 10000,
    "connection_check_interval": 20,
    "max_load_more_clicks": 30,
    "completed_region_threshold": 100,
    "duplicate_exit_threshold": 20,
    "backup_interval": 50,
}

# Browser settings
BROWSER_CONFIG = {
    "user_data_dir": r"C:\playwright",
    "channel": "chrome",
    "headless": True,
    "no_viewport": True,
}

# File paths
PATHS = {
    "data_dir": "../data/data-scrape",
    "backup_folder": "backup",
    "regions_folder": "regions",
    "master_file": "data-scrape.json",
}

# CSS Selectors
SELECTORS = {
    "load_more_link": "a.list__content-load-link",
    "room_card": '[data-testid="kostRoomCard"]',
    "room_name": ".detail-title__room-name",
    "gender": ".detail-kost-overview__gender-box",
    "area": ".detail-kost-overview__area-text",
    "rating": ".detail-kost-overview__rating-text",
    "review_count": ".detail-kost-overview__rating-review",
    "transaction_count": ".detail-kost-overview__total-transaction-text",
    "price": ".rc-price__text",
    "period": ".rc-price__type",
    "address": ".bg-c-text--body-4",
    "facilities": ".detail-kost-facility-item__label",
    "rules": ".detail-kost-rule-item__label",
    "landmark_names": ".landmark-item__text-ellipsis",
    "landmark_distances": ".landmark-item__landmark-distance",
}
