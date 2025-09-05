"""Data parsing and categorization utilities"""

from difflib import SequenceMatcher
from typing import List, Dict


def safe_get_text(page, selector: str) -> str:
    """Safely get text from selector"""
    try:
        element = page.locator(selector).first
        if element.count() > 0:
            return element.inner_text().strip()
        return ""
    except Exception:
        return ""


def safe_get_list(page, selector: str) -> List[str]:
    """Safely get list of text from multiple elements"""
    try:
        elements = page.locator(selector)
        result = []
        for i in range(elements.count()):
            text = elements.nth(i).inner_text().strip()
            if text:
                result.append(text)
        return result
    except Exception:
        return []


def smart_kategorisasi(fasilitas_list: List[str]) -> Dict[str, List[str]]:
    """Categorize facilities using similarity matching"""

    def similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    kategori_templates = {
        "ukuran_listrik": [
            "meter",
            "listrik",
            "termasuk listrik",
            "tidak termasuk listrik",
            "x",
        ],
        "kamar": [
            "kasur",
            "meja",
            "lemari",
            "ac",
            "tv",
            "bantal",
            "cermin",
            "guling",
            "kursi",
            "kipas",
            "ventilasi",
            "jendela",
        ],
        "kamar_mandi": [
            "kloset",
            "shower",
            "wastafel",
            "k. mandi",
            "kamar mandi",
            "ember",
            "bak mandi",
            "air panas",
            "toilet",
        ],
        "umum": [
            "wifi",
            "kulkas",
            "ruang cuci",
            "ruang tamu",
            "ruang jemur",
            "dapur",
            "dispenser",
            "cctv",
            "cleaning",
            "penjaga",
            "mesin cuci",
            "laundry",
            "mushola",
            "jemuran",
            "balcon",
        ],
        "parkir": ["parkir", "motor", "mobil", "sepeda", "garasi"],
    }

    result = {
        "ukuran_listrik": [],
        "kamar": [],
        "kamar_mandi": [],
        "umum": [],
        "parkir": [],
    }

    for fasilitas in fasilitas_list:
        best_category = "umum"  # default fallback
        best_score = 0.3  # minimum threshold

        for category, templates in kategori_templates.items():
            for template in templates:
                score = similarity(fasilitas, template)
                if score > best_score:
                    best_score = score
                    best_category = category

        result[best_category].append(fasilitas)

    return result


def extract_landmarks(page) -> List[Dict[str, str]]:
    """Extract landmark information"""
    landmarks = []
    landmark_names = page.locator(".landmark-item__text-ellipsis")
    landmark_distances = page.locator(".landmark-item__landmark-distance")

    for i in range(landmark_names.count()):
        name = landmark_names.nth(i).inner_text().strip()
        distance = (
            landmark_distances.nth(i).inner_text().strip()
            if i < landmark_distances.count()
            else ""
        )
        landmarks.append({"nama": name, "jarak": distance})

    return landmarks
