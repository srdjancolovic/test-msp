# Imprimatur Sales Dashboard

Streamlit app for consolidating book sales CSV files, visualizing KPIs/charts, and generating AI-powered recommendations with Anthropic Claude.

## Features

- Upload and merge sales data from multiple channels (bookstores, webshop, fairs).
- Interactive dashboard with filters, KPIs, and Plotly charts.
- Export PDF sales report.
- Generate AI recommendations and export them to PDF.

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly
- ReportLab
- Anthropic API

## Requirements

- Python 3.10+ recommended
- Anthropic API key (`ANTHROPIC_API_KEY`) for AI recommendations

## Setup

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from example:

```bash
cp env.example .env
```

4. Add your Anthropic key to `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...
```

## Run the App

```bash
streamlit run app.py
```

Then open the local URL shown in terminal (usually `http://localhost:8501`).

## Input CSV Format

Your CSV files should include at least these columns:

- `Datum`
- `Naslov`
- `Autor`
- `Kolicina`
- `Cijena`
- `Zemlja`

`Kanal` is optional for source-specific uploads (`knjižara`, `web shop`, `sajam`) because the app can infer it from the uploader.

If you want an explicit channel overview from your own channel data, use the dedicated upload:

- `Fajl sa kolonom Kanal` (this one should include `Kanal`).

The app includes a downloadable sample CSV in the **Konsolidacija** tab.

## Notes

- If `ANTHROPIC_API_KEY` is missing, you can still use upload/dashboard features.
- AI recommendations require a valid Anthropic API key.

