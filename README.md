# Kos Price Scraper

Professional web scraper untuk data kos-kosan dari Mamikos dengan arsitektur clean dan modular.

## Features

- ✅ **CLI Arguments** - Professional command line interface
- ✅ **Duplicate Detection** - Smart deduplication with early exit
- ✅ **Network Resilience** - Connection monitoring & timeout handling
- ✅ **Organized Structure** - Modular architecture dengan tools/
- ✅ **Smart Categorization** - AI-powered facility categorization
- ✅ **Backup System** - Auto backup setiap 50 records
- ✅ **Region Management** - Skip completed regions automatically

## Installation

```bash
# Install dependencies
pip install patchright requests

# Install browser
patchright install chromium
```

## Quick Start

```bash
# Navigate to scraper directory
cd backend/scrape

# Normal scraping (continue from backup)
python scrape.py

# Force update all regions
python scrape.py --force-update --verbose

# Scrape specific region
python scrape.py --region jakarta --verbose

# Help
python scrape.py --help
```

## Project Structure

```
backend/
├── scrape/                # Scraper module
│   ├── scrape.py          # Main CLI entrypoint (280 lines)
│   ├── regions.py         # 18 target regions across Indonesia
│   ├── tools/             # Modular utilities
│   │   ├── __init__.py    # Clean import interface
│   │   ├── config.py      # All settings & configurations
│   │   ├── parse_utils.py # Data extraction & categorization
│   │   ├── net_utils.py   # Network monitoring & checks
│   │   ├── dedup_utils.py # Duplicate detection logic
│   │   └── io_utils.py    # File management & backup
│   └── SCRAPER_GUIDE.md   # This documentation
├── data/                  # Organized output structure
│   └── data-scrape/
│       ├── backup/        # Auto backups every 50 records
│       ├── regions/       # Split by region (auto-generated)
│       └── data-scrape.json # Master file with all data
```

## Configuration

All settings in `tools/config.py`:

```python
SCRAPER_CONFIG = {
    "page_timeout": 15000,          # Page load timeout (ms)
    "duplicate_exit_threshold": 20,  # Exit after N consecutive duplicates
    "backup_interval": 50,          # Backup every N records
    "connection_check_interval": 20, # Check connection every N cards
}
```

## Data Output

### Sample Record Structure:

```json
{
  "nama_kos": "Kost Jakarta Premium",
  "jenis_kos": "Campur",
  "harga": "Rp1.500.000",
  "periode": "/bulan",
  "alamat": "Jakarta Selatan, DKI Jakarta",
  "rating": "4.5",
  "fasilitas": {
    "kamar": ["AC", "Kasur", "Lemari"],
    "kamar_mandi": ["Shower", "Kloset Duduk"],
    "umum": ["WiFi", "CCTV", "Dapur"],
    "parkir": ["Parkir Motor"]
  },
  "landmarks": [
    { "nama": "Stasiun MRT", "jarak": "500m" },
    { "nama": "Mall", "jarak": "1.2km" }
  ],
  "region": "jakarta-daerah-khusus-ibukota-jakarta-indonesia",
  "scraped_at": "2025-01-01T10:30:00"
}
```

## CLI Commands

### Basic Usage

```bash
# Continue from last backup
python scrape.py

# Verbose logging
python scrape.py --verbose
```

### Force Update

```bash
# Re-scrape all regions (ignore existing data)
python scrape.py --force-update

# Force update with verbose logging
python scrape.py --force-update --verbose
```

### Single Region

```bash
# Scrape Jakarta only
python scrape.py --region jakarta

# Scrape multiple matching regions
python scrape.py --region bali --verbose
```

### Browser Mode

```bash
# Run with visible browser (debugging)
python scrape.py --no-headless --verbose
```

## Advanced Features

### Smart Duplicate Detection

- ✅ Real-time duplicate checking using `(nama_kos, harga, alamat)` key
- ✅ Early exit after 20 consecutive duplicates
- ✅ Memory efficient comparison

### Network Resilience

- ✅ Internet connection monitoring every 20 cards
- ✅ Timeout handling (15s page load, 10s network idle)
- ✅ Automatic retry and skip failed pages

### Backup System

- ✅ Auto backup every 50 records to `data/backup/`
- ✅ Resume from latest backup automatically
- ✅ Region completion tracking (100+ records = completed)

### Smart Categorization

- ✅ AI-powered facility categorization using similarity matching
- ✅ 5 categories: kamar, kamar_mandi, umum, parkir, ukuran_listrik
- ✅ Fallback to 'umum' category for unknown items

## Performance

### Target Regions (18 cities):

- **Kota Besar:** Jakarta, Bandung, Surabaya, Semarang, Medan, Makassar
- **Kota Pelajar:** Yogyakarta, Malang, Solo, Denpasar, Depok, Bogor
- **Kota Tambahan:** Bekasi, Tangerang, Balikpapan, Pontianak, Palembang, Batam

### Expected Output:

- **~620 records per major city** (Jakarta, Bandung, Surabaya)
- **~200-400 records per smaller city**
- **Total: ~8,000-10,000 records**
- **Runtime: ~60-72 hours** (with delays for politeness)

## Monitoring & Debugging

### Progress Tracking:

```bash
# From backend/scrape directory
ls ../data/data-scrape/backup/ | wc -l

# Latest backup info (Windows)
dir ..\data\data-scrape\backup\ | sort

# Latest backup info (Linux/Mac)
ls -la ../data/data-scrape/backup/ | tail -1
```

Shows:

- 📝 URL being scraped
- 🔄 "Lihat lebih banyak" clicks
- ⚠️ Skipped duplicates
- ❌ Failed page loads
- 🌐 Connection status

## Error Handling

### Automatic Recovery:

- **Connection Lost:** Pause and resume automatically
- **Page Load Timeout:** Skip card and continue
- **403/Error Pages:** Detect and skip automatically
- **Duplicate Data:** Early exit to next region

### Manual Recovery:

```bash
# If script crashes, simply restart
python scrape.py --verbose

# Script will automatically:
# 1. Load latest backup
# 2. Skip completed regions
# 3. Continue from where it left off
```

## Contributing

### Code Architecture:

- **`scrape.py`:** Main flow logic only (~280 lines)
- **`tools/`:** All utilities in separate modules
- **Type hints:** Full typing support for better IDE experience
- **Docstrings:** Comprehensive documentation

### Adding New Features:

1. **New utilities:** Add to appropriate `tools/*.py` file
2. **New configs:** Add to `tools/config.py`
3. **Export:** Update `tools/__init__.py`
4. **Use:** Import in `scrape.py`

## Acknowledgments

Built with:

- **Patchright** - Robust Playwright fork
- **Python 3.8+** - Modern Python features
- **Clean Architecture** - Production-ready structure

---

**Happy Scraping!**
