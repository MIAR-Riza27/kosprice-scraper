import os
import json
import time
import random
from datetime import datetime


def backup_region(region_results, region, backup_round, backup_folder):
    """Backup otomatis data region setiap interval tertentu."""
    backup_path = f"{backup_folder}/{region}_{backup_round}.json"
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(region_results, f, ensure_ascii=False, indent=2)
    print(f"      * [Data Backup: Round {backup_round}]")


def save_region(region_results, region, regions_folder):
    """Simpan data region setelah selesai scraping."""
    region_path = f"{regions_folder}/{region}.json"
    with open(region_path, "w", encoding="utf-8") as f:
        json.dump(region_results, f, ensure_ascii=False, indent=2)
    print(f"      * [Save Data Region: {region}]")


def save_failed_cards(failed_cards_info, region, failed_cards_folder):
    """Simpan info card yang tetap gagal setelah retry ke file khusus."""
    os.makedirs(failed_cards_folder, exist_ok=True)
    failed_path = f"{failed_cards_folder}/{region}_failed.json"
    with open(failed_path, "w", encoding="utf-8") as f:
        json.dump(failed_cards_info, f, ensure_ascii=False, indent=2)
    print(f"      * [Failed cards saved: {failed_path}]")


def scrape_card_detail(card, page, scroll_pause, selectors, parse_utils):
    """Scrape detail satu card, return room_data dict."""
    safe_get_text = parse_utils.safe_get_text
    safe_get_list = parse_utils.safe_get_list
    smart_kategorisasi = parse_utils.smart_kategorisasi
    extract_landmarks = parse_utils.extract_landmarks

    with page.context.expect_page(timeout=10000) as new_page_info:
        card.click()
    new_page = new_page_info.value
    new_page.wait_for_load_state("networkidle", timeout=10000)

    for scroll_pos in scroll_pause:
        new_page.evaluate(
            f"window.scrollTo(0, document.body.scrollHeight*{scroll_pos})"
        )
        time.sleep(random.uniform(1, 2))

    room_data = {
        "nama_kos": safe_get_text(new_page, selectors["room_name"]),
        "jenis_kos": safe_get_text(new_page, selectors["gender"]),
        "area": safe_get_text(new_page, selectors["area"]),
        "rating": safe_get_text(new_page, selectors["rating"]),
        "jumlah_review": safe_get_text(new_page, selectors["review_count"]),
        "total_transaksi": safe_get_text(new_page, selectors["transaction_count"]),
        "harga": safe_get_text(new_page, selectors["price"]),
        "periode": safe_get_text(new_page, selectors["period"]),
        "alamat": safe_get_text(new_page, selectors["address"]),
    }
    fasilitas_list = safe_get_list(new_page, selectors["facilities"])
    room_data["fasilitas"] = smart_kategorisasi(fasilitas_list)
    room_data["peraturan"] = safe_get_list(new_page, selectors["rules"])
    room_data["landmarks"] = extract_landmarks(new_page)
    room_data["url"] = new_page.url
    room_data["scraped_at"] = datetime.now().isoformat()
    new_page.close()
    return room_data


def retry_failed_cards(
    failed_cards,
    page,
    scroll_pause,
    selectors,
    parse_utils,
    dedup,
    seen_keys,
    region_results,
    region,
    backup_interval,
    backup_round,
    backup_folder,
    duplicate_exit_threshold,
):
    """Retry scraping card yang gagal, update region_results dan backup jika berhasil."""
    failed_cards_info = []
    duplicate_count = 0
    for idx, card in failed_cards:
        try:
            room_data = scrape_card_detail(
                card, page, scroll_pause, selectors, parse_utils
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
            print(f"    - Scraped data for kos: {room_data['nama_kos']}")
            if len(region_results) % backup_interval == 0:
                backup_round += 1
                backup_region(region_results, region, backup_round, backup_folder)
        except Exception as e:
            failed_cards_info.append({"idx": idx, "error": str(e)})
    return failed_cards_info, backup_round
