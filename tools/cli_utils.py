import argparse
from tools.config import SCRAPER_CONFIG


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="Daftar region dipisahkan koma. Contoh: --region jakarta-daerah-khusus-ibukota-jakarta-indonesia,bandung-kota-bandung-jawa-barat-indonesia",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Paksa scraping region meskipun sudah ada file region dan jumlah datanya > 150.",
    )
    parser.add_argument(
        "--limit-card",
        type=int,
        default=None,
        help="Batas maksimal card yang di-scrape per region.",
    )
    parser.add_argument(
        "--limit-loadmore",
        type=int,
        default=None,
        help="Override jumlah klik load more per region.",
    )
    parser.add_argument(
        "--backup-interval",
        type=int,
        default=SCRAPER_CONFIG["backup_interval"],
        help="Interval backup otomatis per berapa card.",
    )
    parser.add_argument(
        "--head",
        action="store_true",
        help="Jalankan browser dengan tampilan (non-headless).",
    )
    parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="Matikan deduplication (untuk debugging).",
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=0,
        help="Mulai scraping dari region ke-N (0=awal).",
    )
    parser.add_argument(
        "--start-end",
        type=str,
        default=None,
        help="Range region dari list regions.py, format: start:end (contoh: --start-end 3:5 untuk region ke-3 sampai ke-4, seperti slicing Python).",
    )
    return parser.parse_args()
