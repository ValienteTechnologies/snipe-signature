# Snipe Sign

Generate printable PDF checkout and return forms for [Snipe-IT](https://snipeitapp.com/) assets, ready for physical signature.

## Features

- Look up assets by tag, or search users by name/username/email with live autocomplete
- Generate checkout and return forms as PDF (opens in browser for printing) or DOCX (download)
- Two document templates: **Eve** and **Uwagi**
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
| `RFID_PRINTER_URL` | No | — | Internal RFID printer service URL (see below) |

## RFID Printer

When `RFID_PRINTER_URL` is set, the app exposes two ways to print RFID labels:

**Single tag** — a printer icon button appears in each row of the asset table on the preview page. Click it to send that asset's tag to the printer.

**Range** — on the home page, type a range into the asset search box (e.g. `00001-00010`) and press Enter. The app prints each tag in sequence and shows live progress. Tags must be zero-padded numeric; maximum 1000 tags per range.

The app proxies print requests to the configured service:

```
POST {RFID_PRINTER_URL}
Content-Type: application/json

{"tag": "00001"}
```

The printer service's response is passed back to the UI and displayed to the user.
