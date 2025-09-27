from patchright.sync_api import sync_playwright
import os
import sys
import json
import random
import time

from regions import regions
from tools.config import SCRAPER_CONFIG, BROWSER_CONFIG, PATHS, SELECTORS
from tools.cli_utils import parse_args
from tools.net_utils import check_internet
from tools import parse_utils
from tools.scrape_utils import (
    backup_region,
    save_region,
    save_failed_cards,
    scrape_card_detail,
    retry_failed_cards,
)


def scrape_mamikos_single(
    region_list,
    force=False,
    limit_card=None,
    limit_loadmore=None,
    backup_interval=None,
    dedup=True,
):
    browser = (
        sync_playwright()
        .start()
        .chromium.launch_persistent_context(
            user_data_dir=BROWSER_CONFIG["user_data_dir"],
            channel=BROWSER_CONFIG["channel"],
            headless=BROWSER_CONFIG["headless"],
            no_viewport=BROWSER_CONFIG["no_viewport"],
        )
    )
    results = []
    seen_keys = set()

    backup_interval = (
        backup_interval
        if backup_interval is not None
        else SCRAPER_CONFIG["backup_interval"]
    )
    max_loadmore = (
        limit_loadmore
        if limit_loadmore is not None
        else SCRAPER_CONFIG["max_load_more_clicks"]
    )
    completed_region_threshold = SCRAPER_CONFIG["completed_region_threshold"]
    scroll_pause = SCRAPER_CONFIG.get("scroll_pause", [1 / 3, 2 / 3, 1, 0])
    max_card_retry = SCRAPER_CONFIG.get("max_card_retry", 2)
    duplicate_exit_threshold = SCRAPER_CONFIG.get("duplicate_exit_threshold", 20)

    for region in region_list:
        print("+===+ \n \n+===+")
        # Cek koneksi internet sebelum scraping region, maksimal 3 kali
        retry_count = 0
        max_retry = SCRAPER_CONFIG.get("max_connection_retry", 3)
        while not check_internet():
            retry_count += 1
            print("  X [ERROR: No Internet Connection | Retrying in 10 seconds]")
            if retry_count >= max_retry:
                print(f"  X [FATAL: Failed to connect | Max attempts: {max_retry}]")
                print(
                    "    > Make sure your computer is connected to the internet, then restart the scraper"
                )
                print(
                    "+===+ \n \n+===+ \n# Scraping Canceled: No Internet Connection\n+===+ \n \n+===+"
                )
                browser.close()
                sys.exit(1)
            time.sleep(SCRAPER_CONFIG.get("internet_retry_sleep", 10))
        region_path = f"{PATHS['regions_folder']}/{region}.json"
        skip_region = False
        if os.path.exists(region_path):
            try:
                with open(region_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                if (
                    isinstance(existing_data, list)
                    and len(existing_data) > completed_region_threshold
                    and not force
                ):
                    print(
                        f"  X [Skip Region: {region} | Sum Data: {len(existing_data)}]"
                    )
                    skip_region = True
            except Exception as e:
                print(f"  X [Warning: Fail to read {region}: {e}]")
        if skip_region:
            continue

        page = browser.new_page()
        print(f"# Scraping region: {region}")

        url = SCRAPER_CONFIG["url_template"].format(
            base_url=SCRAPER_CONFIG["base_url"], region=region
        )

        try:
            page.goto(url, timeout=SCRAPER_CONFIG["page_timeout"])
        except Exception as e:
            print(f"    X [Error opening region: {e} | URL: {url}]")
            continue

        # Klik load more jika ada
        loadmore_count = 0
        while True:
            try:
                page.wait_for_selector(
                    SELECTORS["load_more_link"], timeout=SCRAPER_CONFIG["load_timeout"]
                )
                page.locator(SELECTORS["load_more_link"]).scroll_into_view_if_needed()
                page.click(
                    SELECTORS["load_more_link"], timeout=SCRAPER_CONFIG["page_timeout"]
                )
                loadmore_count += 1
                print(f"    * [Load More: {loadmore_count}]")
                time.sleep(random.uniform(1, 4))
                if loadmore_count >= max_loadmore:
                    print(f"    * [Max Load More reached: {max_loadmore}]")
                    break
            except Exception:
                break

        page.wait_for_selector(
            SELECTORS["room_card"],
            timeout=SCRAPER_CONFIG["load_timeout"],
            state="attached",
        )
        cards = page.locator(SELECTORS["room_card"]).all()
        print(f"  > Found {len(cards)} cards")

        region_results = []
        backup_round = 0
        card_iter = cards[:limit_card] if limit_card else cards
        duplicate_count = 0
        failed_cards = []
        failed_cards_info = []

        # --- LOOP UTAMA: SCRAPE CARD ---
        for idx, card in enumerate(card_iter):
            try:
                room_data = scrape_card_detail(
                    card, page, scroll_pause, SELECTORS, parse_utils
                )
                dedup_key = (
                    room_data["nama_kos"].strip().lower(),
                    room_data["area"].strip().lower(),
                    room_data["alamat"].strip().lower(),
                )
                if dedup and dedup_key in seen_keys:
                    print(
                        f"    X [DUPLICATE: {room_data['nama_kos']} ({room_data['area']} - {room_data['alamat']})]"
                    )
                    duplicate_count += 1
                    if duplicate_count > duplicate_exit_threshold:
                        print(
                            "    X [Terlalu banyak duplikat, scraping region dihentikan!]"
                        )
                        break
                    continue
                seen_keys.add(dedup_key)
                region_results.append(room_data)
                results.append(room_data)
                print(f"    - Scraped data for kos: {room_data['nama_kos']}")
                if len(region_results) % backup_interval == 0:
                    backup_round += 1
                    backup_region(
                        region_results, region, backup_round, PATHS["backup_folder"]
                    )
            except Exception as e:
                print(f"    X [Error scraping card: {e}]")
                failed_cards.append((idx, card))
                failed_cards_info.append({"idx": idx, "error": str(e)})
                continue

        # --- RETRY CARD GAGAL ---
        for retry in range(1, max_card_retry):
            if not failed_cards:
                break
            print(f"Retrying {len(failed_cards)} failed cards, attempt {retry + 1}")
            failed_cards_info_retry, backup_round = retry_failed_cards(
                failed_cards,
                page,
                scroll_pause,
                SELECTORS,
                parse_utils,
                dedup,
                seen_keys,
                region_results,
                region,  # <-- tambahkan ini
                backup_interval,
                backup_round,
                PATHS["backup_folder"],
                duplicate_exit_threshold,
            )
            failed_cards_info.extend(failed_cards_info_retry)
            failed_cards = [
                fc
                for fc in failed_cards
                if fc[0] in [info["idx"] for info in failed_cards_info_retry]
            ]

        # --- SIMPAN DATA REGION & FAILED CARDS ---
        save_region(region_results, region, PATHS["regions_folder"])
        if failed_cards_info:
            save_failed_cards(failed_cards_info, region, PATHS["failed_cards_folder"])

        page.close()

    browser.close()
    return results


if __name__ == "__main__":
    args = parse_args()
    # Pilih region
    if args.region:
        region_list = [r.strip() for r in args.region.split(",") if r.strip()]
    else:
        region_list = regions

    # Slicing region jika --start-end diberikan
    if args.start_end:
        try:
            start, end = args.start_end.split(":")
            start = int(start) if start else None
            end = int(end) if end else None
            region_list = region_list[start:end]
        except Exception:
            print(
                "  X [ERROR Format --start-end: (start:end), Example: --start-end 3:5]"
            )
            sys.exit(1)

    # Start from region ke-N
    region_list = region_list[args.start_from :]

    # Set headless mode
    BROWSER_CONFIG["headless"] = not args.head

    products = scrape_mamikos_single(
        region_list,
        force=args.force,
        limit_card=args.limit_card,
        limit_loadmore=args.limit_loadmore,
        backup_interval=args.backup_interval,
        dedup=not args.no_dedup,
    )

    print("+===+ \n \n+===+ \n# Scrape Done ;)")

    output_path = f"{PATHS['data_dir']}/{PATHS['master_file']}"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"  * [Data Master: Saved to {output_path}] \n+===+ \n \n+===+")

# ingat:
# Argumen Command Line (argparse)
# Deduplication {Selesai}
# Cek Koneksi Internet {Selesai}
# Penyimpanan Data Per Region & Backup {Selesai}
# Memory Cleanup {Selesai}
# Scraped Timestamp {Selesai}
# Verbose Logging {menurutku sudah cukup}
# Save Master File & Struktur Folder Otomatis {sudah ada tinggal dipake}
# Scrape few / Multi-region Otomatis {Selesai}
# config {PATHS, SCRAPER_CONFIG, BROWSER_CONFIG, SELECTORS} {Selesai}
# ---
