"""Scraping tools and utilities"""

from .parse_utils import (
    safe_get_text,
    safe_get_list,
    smart_kategorisasi,
    extract_landmarks,
)

from .net_utils import check_internet_connection, check_connection_periodically

from .dedup_utils import is_duplicate, remove_duplicates, count_duplicates

from .io_utils import (
    load_backup_data,
    save_backup,
    save_master_file,
    save_by_regions,
    ensure_directories,
)

from .config import SCRAPER_CONFIG, BROWSER_CONFIG, PATHS, SELECTORS

__all__ = [
    # Parse utilities
    "safe_get_text",
    "safe_get_list",
    "smart_kategorisasi",
    "extract_landmarks",
    # Network utilities
    "check_internet_connection",
    "check_connection_periodically",
    # Deduplication utilities
    "is_duplicate",
    "remove_duplicates",
    "count_duplicates",
    # IO utilities
    "load_backup_data",
    "save_backup",
    "save_master_file",
    "save_by_regions",
    "ensure_directories",
    # Configuration
    "SCRAPER_CONFIG",
    "BROWSER_CONFIG",
    "PATHS",
    "SELECTORS",
]
