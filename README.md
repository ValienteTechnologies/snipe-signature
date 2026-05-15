# Snipe Sign

Generate printable PDF checkout and return forms for [Snipe-IT](https://snipeitapp.com/) assets, ready for physical signature.

## Features

- Look up assets by tag, or search users by name/username/email with live autocomplete
- Generate checkout and return forms as PDF (opens in browser for printing) or DOCX (download)
- Two document templates: **Eve** and **Unagi**
- Turkish and English language support
- Custom logo branding per deployment
- Cloudflare Access support for protected Snipe-IT instances
- RFID label printer integration — print a single tag from the asset table, or a range directly from the search box

## Requirements

- Docker (recommended) or Python 3.11+
- A running Snipe-IT instance with an API token

## Quick Start

### Docker

```bash
cp .env.example .env
# edit .env with your values
docker compose up -d
```

The app will be available at `http://localhost:8000`.

### Local

```bash
python -m venv venv && source venv/bin/activate
pip install -e .
cp .env.example .env
# edit .env with your values
uvicorn app.main:app --reload
```

## Configuration

All configuration is via environment variables (or a `.env` file):

| Variable | Required | Default | Description |
|---|---|---|---|
| `SNIPEIT_URL` | Yes | — | Base URL of your Snipe-IT instance |
| `SNIPEIT_TOKEN` | Yes | — | Snipe-IT API token |
| `SNIPEIT_VERIFY_SSL` | No | `true` | Verify SSL certificates |
| `CF_ACCESS_CLIENT_ID` | No | — | Cloudflare Access client ID |
| `CF_ACCESS_CLIENT_SECRET` | No | — | Cloudflare Access client secret |
| `APP_LANG` | No | `en` | UI and document language (`en` or `tr`) |
| `APP_PORT` | No | `8000` | Port to listen on |
| `LOGO_PATH` | No | — | Absolute path to a logo image for documents |
| `DOC_FOOTER_TEXT` | No | — | Footer text printed on every generated document |
| `SATO_PRINTER_IP` | No | — | IP address of the SATO RFID label printer (leave blank to disable) |
| `SATO_PRINTER_PORT` | No | `9100` | TCP port of the SATO printer |
| `SATO_QR_BASE_URL` | No | — | Base URL for QR codes on labels (asset ID is appended, e.g. `https://snipeit.example.com/hardware/`) |

## RFID Printer

When `SATO_PRINTER_IP` is set, the app communicates directly with the SATO label printer over raw TCP (SBPL protocol) and exposes two ways to print RFID labels:

**Single tag** — a printer icon button appears in each row of the asset table on the preview page. Click it to print that asset's label. The printer's response is shown inline next to the button.

**Range** — on the home page, type a range into the asset search box (e.g. `00001-00010`) and press Enter. The app prints each tag in sequence and shows live progress. Tags must be zero-padded numeric; maximum 1000 tags per range.
