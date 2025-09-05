"""Clean, modular version of the scraper"""

from patchright.sync_api import sync_playwright
import time
import os
import random
import argparse
from datetime import datetime

from regions import regions
from tools import (
    # Config
    SCRAPER_CONFIG,
    BROWSER_CONFIG,
    PATHS,
    SELECTORS,
    # Parse utilities
    safe_get_text,
    safe_get_list,
    smart_kategorisasi,
    extract_landmarks,
    # Network utilities
    check_internet_connection,
    # Deduplication
    is_duplicate,
    # IO utilities
    load_backup_data,
    save_backup,
    save_master_file,
    save_by_regions,
)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Kos Price Scraper")
    parser.add_argument(
        "--force-update",
        "--update",
        action="store_true",
        help="Re-scrape all regions ignoring existing data",
    )
    parser.add_argument(
        "--region", type=str, help="Scrape specific region only (e.g., jakarta)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode",
    )
    return parser.parse_args()


def load_existing_data(force_update=False):
    """Load existing backup data to continue scraping"""
    if force_update:
        print("🔄 FORCE UPDATE MODE - Will re-scrape all regions")
        return [], set()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, PATHS["data_dir"])
    backup_dir = os.path.join(data_dir, PATHS["backup_folder"])

    return load_backup_data(backup_dir)


def extract_room_data(new_page, region):
    """Extract room data from detail page"""
    # Basic info using config selectors
    room_data = {
        "nama_kos": safe_get_text(new_page, SELECTORS["room_name"]),
        "jenis_kos": safe_get_text(new_page, SELECTORS["gender"]),
        "area": safe_get_text(new_page, SELECTORS["area"]),
        "rating": safe_get_text(new_page, SELECTORS["rating"]),
        "jumlah_review": safe_get_text(new_page, SELECTORS["review_count"]),
        "total_transaksi": safe_get_text(new_page, SELECTORS["transaction_count"]),
        "harga": safe_get_text(new_page, SELECTORS["price"]),
        "periode": safe_get_text(new_page, SELECTORS["period"]),
        "alamat": safe_get_text(new_page, SELECTORS["address"]),
    }

    # Fasilitas dengan smart kategorisasi
    fasilitas_list = safe_get_list(new_page, SELECTORS["facilities"])
    room_data["fasilitas"] = smart_kategorisasi(fasilitas_list)

    # Peraturan
    room_data["peraturan"] = safe_get_list(new_page, SELECTORS["rules"])

    # Landmarks
    room_data["landmarks"] = extract_landmarks(new_page)

    # Meta data
    room_data["region"] = region
    room_data["url"] = new_page.url
    room_data["scraped_at"] = datetime.now().isoformat()

    return room_data


def scrape_region(page, region, all_rooms_data, args):
    """Scrape a single region"""
    region_keywords = region.split("-")[0]
    url = SCRAPER_CONFIG["url_template"].format(
        base_url=SCRAPER_CONFIG["base_url"], region=region, keyword=region_keywords
    )

    if args.verbose:
        print(f"📝 URL: {url}")

    page.goto(url)

    # Load more cards
    for more_rooms in range(SCRAPER_CONFIG["max_load_more_clicks"]):
        try:
            page.wait_for_selector(SELECTORS["load_more_link"], timeout=10000)
            link = page.locator(SELECTORS["load_more_link"])

            if link.count() > 0 and link.is_visible():
                link.scroll_into_view_if_needed()
                link.click()
                time.sleep(random.uniform(1, 2))
                print(f"    ✅ Clicked 'Lihat lebih banyak' #{more_rooms + 1}")
            else:
                print("    ℹ️ No more 'Lihat lebih banyak' link, stopping expansion")
                break
        except Exception as e:
            print(f"    ℹ️ No more pages to load: {str(e)[:50]}...")
            break

    time.sleep(random.uniform(2, 4))

    cards = page.locator(SELECTORS["room_card"]).all()
    print(f"Found {len(cards)} cards in region {region}")

    consecutive_duplicates = 0

    for i, card in enumerate(cards):
        # Connection check
        if i % SCRAPER_CONFIG["connection_check_interval"] == 0 and i > 0:
            if not check_internet_connection():
                print(f"❌ Connection lost at card {i}. Moving to next region...")
                break

        time.sleep(random.uniform(1, 3))

        # Open detail page with timeout handling
        try:
            with page.context.expect_page(
                timeout=SCRAPER_CONFIG["page_timeout"]
            ) as new_page_info:
                card.click()
            new_page = new_page_info.value
        except Exception as e:
            if args.verbose:
                print(f"⚠️ Failed to open card {i + 1}: {str(e)[:50]}... Skipping...")
            continue

        # Check page load
        try:
            new_page.wait_for_load_state(
                "networkidle", timeout=SCRAPER_CONFIG["load_timeout"]
            )

            if any(
                error in new_page.title() for error in ["403", "Forbidden", "Error"]
            ):
                if args.verbose:
                    print("❌ Error page detected, skipping...")
                new_page.close()
                continue
        except Exception as e:
            if args.verbose:
                print(f"❌ Page load timeout: {str(e)[:50]}... Skipping...")
            new_page.close()
            continue

        # Human-like scrolling
        for scroll_pos in [1 / 3, 2 / 3, 1, 0]:
            new_page.evaluate(
                f"window.scrollTo(0, document.body.scrollHeight*{scroll_pos})"
            )
            time.sleep(random.uniform(1, 2))

        # Extract data
        room_data = extract_room_data(new_page, region)

        # Check duplicates
        if not is_duplicate(room_data, all_rooms_data):
            all_rooms_data.append(room_data)
            print(f"✅ Extracted: {room_data['nama_kos']} - {room_data['harga']}")
            consecutive_duplicates = 0
        else:
            if args.verbose:
                print(f"⚠️ Skipped duplicate: {room_data['nama_kos']}")
            consecutive_duplicates += 1

            if consecutive_duplicates >= SCRAPER_CONFIG["duplicate_exit_threshold"]:
                print(
                    f"🛑 Region exhausted ({consecutive_duplicates} consecutive duplicates)"
                )
                current_region_count = len(
                    [r for r in all_rooms_data if r.get("region") == region]
                )
                print(
                    f"📊 Total extracted from {region}: {current_region_count} records"
                )
                new_page.close()
                break

        # Backup periodically
        if len(all_rooms_data) % SCRAPER_CONFIG["backup_interval"] == 0:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(script_dir, PATHS["data_dir"])
            backup_dir = os.path.join(data_dir, PATHS["backup_folder"])
            save_backup(all_rooms_data, backup_dir)

        time.sleep(random.uniform(2, 4))
        new_page.close()

    return all_rooms_data


def scrape(playwright, args):
    """Main scraping function"""
    all_rooms_data, completed_regions = load_existing_data(args.force_update)

    browser = playwright.chromium.launch_persistent_context(
        user_data_dir=BROWSER_CONFIG["user_data_dir"],
        channel=BROWSER_CONFIG["channel"],
        headless=args.headless,
        no_viewport=BROWSER_CONFIG["no_viewport"],
    )

    page = browser.new_page()

    # Filter regions
    regions_to_process = regions
    if args.region:
        matching_regions = [r for r in regions if args.region.lower() in r.lower()]
        if matching_regions:
            regions_to_process = matching_regions
            print(
                f"🎯 Found {len(matching_regions)} matching regions for '{args.region}'"
            )
        else:
            print(f"❌ No regions found matching '{args.region}'")
            return []

    for region in regions_to_process:
        if not args.force_update and region in completed_regions:
            print(f"⏭️ Skipping completed region: {region}")
            continue

        print(f"🎯 Processing region: {region}")

        if args.verbose:
            print(
                f"📝 Starting scrape for {region} with {len(all_rooms_data)} existing records"
            )

        all_rooms_data = scrape_region(page, region, all_rooms_data, args)

        # Memory cleanup every 5 regions
        if (
            regions_to_process.index(region) % 5 == 0
            and regions_to_process.index(region) > 0
        ):
            print("🔄 Memory cleanup...")
            page.close()
            page = browser.new_page()
            time.sleep(random.uniform(10, 20))

        print(f"📝 Completed region {region}. Taking a break...")
        time.sleep(random.uniform(5, 10))

    browser.close()
    return all_rooms_data


if __name__ == "__main__":
    args = parse_arguments()

    if args.force_update:
        print("🚀 FORCE UPDATE MODE - Re-scraping all regions")
    if args.region:
        print(f"🎯 SINGLE REGION MODE - Scraping {args.region} only")
    if args.verbose:
        print("📝 VERBOSE MODE - Detailed logging enabled")

    with sync_playwright() as playwright:
        all_rooms_data = scrape(playwright, args)

    # Save results
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, PATHS["data_dir"])
    master_filepath = os.path.join(data_dir, PATHS["master_file"])

    save_master_file(all_rooms_data, master_filepath)
    save_by_regions(all_rooms_data, data_dir)

    print(f"📊 Total rooms scraped: {len(all_rooms_data)}")
    print("📁 File structure created:")
    print("   /data-scrape/")
    print("   ├── /backup/")
    print("   ├── /regions/")
    print("   └── data-scrape.json")
    print("✅ Scraping completed successfully!")
