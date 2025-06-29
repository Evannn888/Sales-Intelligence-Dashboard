# Sales Intelligence Dashboard

A simple dashboard for analyzing company visits and lead scores from web logs.

## Quick Start

1. **Generate Logs:**
   ```sh
   python3 generate_logs.py
   ```
2. **Process Logs:**
   ```sh
   python3 process_logs.py
   ```
3. **View Dashboard:**
   - Start a local server:
     ```sh
     python3 -m http.server 8000
     ```
   - Open [http://localhost:8000/index.html](http://localhost:8000/index.html) in your browser.

## Files
- `access.log` - Fake web logs.
- `generate_logs.py` — Generates fake web logs.
- `process_logs.py` — Parses logs, enriches IPs, scores leads, outputs `visitorData.json`.
- `index.html` — Dashboard UI (uses Tailwind CDN and inline JS).
- `visitorData.json` — Output data for the dashboard.

## Requirements
- Python 3.x
- Internet connection (for IP enrichment and Tailwind CDN)