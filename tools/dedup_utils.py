"""Duplicate detection utilities"""

from typing import List, Dict, Any, Tuple


def create_data_key(data: Dict[str, Any]) -> Tuple[str, str, str]:
    """Create a unique key for data comparison"""
    return (
        data.get("nama_kos", ""),
        data.get("harga", ""),
        data.get("alamat", ""),
    )


def is_duplicate(new_data: Dict[str, Any], existing_data: List[Dict[str, Any]]) -> bool:
    """Check if data already exists in the dataset"""
    new_key = create_data_key(new_data)

    for existing in existing_data:
        existing_key = create_data_key(existing)
        if new_key == existing_key:
            return True
    return False


def remove_duplicates(data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicates from a list of data"""
    seen_keys = set()
    unique_data = []

    for item in data_list:
        key = create_data_key(item)
        if key not in seen_keys:
            seen_keys.add(key)
            unique_data.append(item)

    return unique_data


def count_duplicates(data_list: List[Dict[str, Any]]) -> int:
    """Count number of duplicates in dataset"""
    total_items = len(data_list)
    unique_items = len(remove_duplicates(data_list))
    return total_items - unique_items
