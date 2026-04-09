# Snipe Sign

> https://github.com/ValienteTechnologies/snipe-sign

Generate printable PDF checkout and return forms for [Snipe-IT](https://snipeitapp.com/) assets, ready for physical signature.

## Features

- Look up assets or users from your Snipe-IT instance
- Generate checkout and return forms as PDFs
- Two document templates: **Eve** and **Uwagi**
- Turkish and English language support
- Custom logo branding per deployment
- Cloudflare Access support for protected Snipe-IT instances

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
