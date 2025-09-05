"""Input/Output utilities for data management"""

import json
import os
from typing import List, Dict, Any, Tuple, Set


def ensure_directories(*paths: str) -> None:
    """Ensure directories exist"""
    for path in paths:
        os.makedirs(path, exist_ok=True)


def get_latest_backup_file(backup_dir: str) -> str:
    """Get the latest backup file from backup directory"""
    try:
        backup_files = [
            f for f in os.listdir(backup_dir) if f.startswith("data-scrape_backup_")
        ]
        if backup_files:
            return max(
                backup_files,
                key=lambda x: int(x.split("_")[-1].split(".")[0]),
            )
    except Exception:
        pass
    return ""


def load_backup_data(backup_dir: str) -> Tuple[List[Dict[str, Any]], Set[str]]:
    """Load existing backup data and determine completed regions"""
    ensure_directories(backup_dir)

    latest_backup = get_latest_backup_file(backup_dir)
    if not latest_backup:
        return [], set()

    backup_path = os.path.join(backup_dir, latest_backup)

    try:
        with open(backup_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)

        # Count records per region
        region_counts = {}
        for item in existing_data:
            if "region" in item and item["region"]:
                region_counts[item["region"]] = region_counts.get(item["region"], 0) + 1

        # Regions with 100+ records are considered completed
        completed_regions = {
            region for region, count in region_counts.items() if count >= 100
        }

        print(
            f"📂 Loaded {len(existing_data)} existing records from backup/{latest_backup}"
        )
        print(f"📊 Region counts: {region_counts}")
        print(f"✅ Completed regions (100+ records): {list(completed_regions)}")

        return existing_data, completed_regions

    except Exception as e:
        print(f"❌ Error loading backup: {e}")
        return [], set()


def save_backup(data: List[Dict[str, Any]], backup_dir: str) -> None:
    """Save backup file"""
    ensure_directories(backup_dir)

    filename = f"data-scrape_backup_{len(data)}.json"
    filepath = os.path.join(backup_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"🔄 Backup saved: backup/{filename}")


def save_master_file(data: List[Dict[str, Any]], filepath: str) -> None:
    """Save master data file"""
    ensure_directories(os.path.dirname(filepath))

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("💾 Master file saved: data-scrape.json")


def save_by_regions(all_data: List[Dict[str, Any]], data_dir: str) -> None:
    """Split and save data by regions"""
    regions_dir = os.path.join(data_dir, "regions")
    ensure_directories(regions_dir)

    by_region = {}
    for item in all_data:
        region = item.get("region", "unknown")
        region_name = region.split("-")[0]  # jakarta, bandung, etc.

        if region_name not in by_region:
            by_region[region_name] = []
        by_region[region_name].append(item)

    for region_name, data in by_region.items():
        filename = f"data-scrape-{region_name}.json"
        filepath = os.path.join(regions_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"📁 Saved {len(data)} records to regions/{filename}")
