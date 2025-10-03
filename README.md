# KosPrice Scraper – Web Scraper Modular untuk Data Kos Indonesia

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Patchright-2EAD33?style=for-the-badge" alt="Patchright">
  <img src="https://img.shields.io/badge/Web%20Scraping-4B8BBE?style=for-the-badge" alt="Web Scraping">
</p>

> **KosPrice Scraper** adalah modul web scraping modular dan production-ready untuk mengumpulkan data kos/kontrakan dari platform populer (Mamikos). Dirancang untuk pipeline data real estate, riset, dan machine learning.

---

## Fitur Utama

- **Modular & Maintainable**: Struktur kode terpisah (tools, config, logic utama)
- **Multi-Region**: Scraping otomatis banyak kota besar Indonesia
- **Smart Retry**: Card yang gagal scrape otomatis dicoba ulang (retry)
- **Backup Otomatis**: Data di-backup per interval, anti data hilang
- **Deduplication**: Data duplikat otomatis di-skip
- **Configurable**: Semua pengaturan lewat satu file config
- **CLI Powerful**: Banyak argumen untuk kontrol scraping
- **Error Handling**: Card gagal disimpan untuk analisis/manual scrape

---


## Struktur Folder

```
scraper/
├── data/
│   ├── backup/         # Backup otomatis per region
│   ├── regions/        # Data hasil scrape per region
│   └── data-scraper.json # Data master hasil scraping
├── tools/
│   ├── config.py       # Semua konfigurasi scraper
│   ├── cli_utils.py    # Argparse & CLI helper
│   ├── net_utils.py    # Cek koneksi internet
│   ├── parse_utils.py  # Parsing & kategorisasi data
│   └── scrape_utils.py # Backup, retry, save, dsb
├── regions.py          # Daftar region/kota target scraping
├── scraper.py          # Main entry point scraper
└── README.md
```

---

## Setup & Instalasi

### 1. Clone Repo
```bash
git clone https://github.com/MIAR-Riza27/kos-price-scraper.git
cd kos-price-scraper
```

### 2. Buat Virtual Environment (Opsional tapi Disarankan)
```bash
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```



### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan Scraper

### Basic Usage
```bash
python scraper.py
```
- Akan scrape semua region default di `regions.py` dengan setting default.

### Argumen CLI Penting
| Argumen           | Fungsi                                                                                   |
|-------------------|-----------------------------------------------------------------------------------------|
| `--region`        | Pilih region tertentu (pisahkan koma)                                                   |
| `--force`         | Paksa scraping meski file region sudah ada                                              |
| `--limit-card`    | Batas maksimal card yang di-scrape per region                                           |
| `--limit-loadmore`| Override jumlah klik load more per region                                               |
| `--backup-interval`| Interval backup otomatis (default dari config)                                         |
| `--head`          | Jalankan browser dengan tampilan GUI (non-headless)                                     |
| `--no-dedup`      | Matikan deduplication (untuk debugging)                                                 |
| `--start-from`    | Mulai scraping dari region ke-N (0=awal)                                                |
| `--start-end`     | Range region, format: start:end (contoh: --start-end 3:5 untuk region ke-3 sampai ke-4) |

**Contoh:**
```bash
python scraper.py --region jakarta-daerah-khusus-ibukota-jakarta-indonesia,bandung-kota-bandung-jawa-barat-indonesia --limit-card 100 --backup-interval 20
```

---

## Konfigurasi

Semua pengaturan utama ada di `tools/config.py`:

- **SCRAPER_CONFIG**: timeout, retry, backup, dedup, dsb.
- **PATHS**: lokasi folder data, backup, failed, dsb.
- **SELECTORS**: selector CSS untuk scraping.
- **BROWSER_CONFIG**: pengaturan browser Playwright.

**Ubah sesuai kebutuhan workflow-mu!**

---


## Output Data

- **Per region**: `data/regions/<region>.json`
- **Backup**: `data/backup/<region>_<round>.json`
- **Master file**: `data/data-scraper.json`

---

## Cara Kerja Scraper

1. **Ambil daftar region** dari `regions.py`
2. **Scrape semua card** di setiap region (klik load more otomatis)
3. **Deduplication**: Data duplikat di-skip
4. **Backup otomatis** setiap interval card berhasil
5. **Retry otomatis** untuk card yang gagal scrape
6. **Card gagal setelah retry** hanya dicatat di log (tidak ada folder khusus)
7. **Data master** digabung dan disimpan di `data/data-scraper.json`

---

## Tips & Catatan

- **Jangan scraping pakai kuota/pulsa** (bisa sangat boros!)
- Untuk testing, gunakan `--limit-card` dan region kecil.
- Jika scraping besar, gunakan server/VPS atau WiFi unlimited.
- Jika ingin scraping platform lain, tinggal ganti selector & logic di tools.

---

## Kontribusi

Pull request, issue, dan diskusi sangat terbuka!  
Silakan fork, modifikasi, dan submit PR untuk fitur baru, bugfix, atau dokumentasi.

---

## Lisensi & Credits

- **License**: MIT License
- **Author**: Muhammad Ibnu Alvariza - [@MIAR-Riza27](https://github.com/MIAR-Riza27)
- **Tech Stack**: Python, Patchright
- **Data Source**: Web scraping (for educational purposes)

---

> **Disclaimer**: Scraper ini dibuat untuk tujuan edukasi dan riset. Gunakan data dengan bijak dan sesuai aturan platform sumber.