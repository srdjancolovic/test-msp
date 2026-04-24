import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from anthropic import Anthropic
import io
import os
import hashlib
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from dotenv import load_dotenv

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Imprimatur — Dashboard prodaje",
    page_icon="I",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --bg: #0B1020;
    --surface: #121A31;
    --surface-soft: #1A2442;
    --primary: #6C63FF;
    --primary-soft: #8D86FF;
    --accent: #00D4FF;
    --text: #E6ECFF;
    --muted: #A7B3D4;
    --success: #00C48C;
    --border: rgba(167, 179, 212, 0.2);
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background: radial-gradient(circle at 10% 10%, #19284f 0%, var(--bg) 45%);
    color: var(--text);
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 1400px; }

section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top right, rgba(108,99,255,.20), transparent 45%),
        linear-gradient(180deg, #0f1630 0%, #0b1020 100%);
    border-right: 1px solid var(--border);
}

/* Keep navigation always visible on desktop */
@media (min-width: 769px) {
    section[data-testid="stSidebar"] {
        min-width: 290px !important;
        max-width: 290px !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        margin-left: 0 !important;
        transform: translateX(0) !important;
    }
    [data-testid="collapsedControl"] {
        display: block !important;
    }
}

section[data-testid="stSidebar"] * {
    color: var(--text);
}

[data-testid="stSidebar"] .stRadio label {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    padding: .35rem .6rem;
    margin-bottom: .25rem;
    transition: all .2s ease;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(108,99,255,.12);
    border-color: rgba(108,99,255,.35);
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(108,99,255,.25);
    border-color: rgba(0,212,255,.55);
}
[data-testid="stSidebar"] .stMarkdown p {
    color: var(--muted);
    font-size: .85rem;
}

/* ── Hero header ── */
.hero {
    background: linear-gradient(130deg, #6C63FF 0%, #4F46E5 50%, #00D4FF 100%);
    border-radius: 18px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.28);
}
.hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(120deg, rgba(255,255,255,.18), rgba(255,255,255,0));
}
.hero h1 {
    font-size: 2.1rem;
    font-weight: 800;
    color: #ffffff !important;
    margin: 0 0 .3rem 0;
    letter-spacing: .01em;
}
.hero p {
    color: rgba(255,255,255,.85);
    font-size: 1rem;
    margin: 0;
    font-weight: 500;
}

/* ── KPI cards ── */
.kpi-card {
    background: linear-gradient(180deg, rgba(26,36,66,.95), rgba(18,26,49,.95));
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    box-shadow: 0 10px 24px rgba(0,0,0,.25);
}
.kpi-label {
    font-size: .72rem;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .3rem;
}
.kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #F8FAFF;
    line-height: 1;
}

/* ── Section headers ── */
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    border-bottom: 1px solid var(--border);
    padding-bottom: .45rem;
    margin: 1.4rem 0 .9rem 0;
}

/* ── Upload area ── */
.upload-hint {
    background: rgba(26,36,66,.8);
    border: 1px dashed rgba(0,212,255,.35);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    font-size: .9rem;
    color: var(--muted);
    margin-bottom: .8rem;
}

/* ── AI box ── */
.ai-box {
    background: rgba(26,36,66,.9);
    border: 1px solid rgba(108,99,255,.4);
    border-radius: 14px;
    padding: 1.4rem 1.7rem;
    box-shadow: 0 8px 30px rgba(0,0,0,.3);
    white-space: pre-wrap;
    font-size: .95rem;
    line-height: 1.7;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #6C63FF, #00D4FF) !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: .03em !important;
    font-size: .85rem !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    border-radius: 10px !important;
    padding: .58rem 1.2rem !important;
    transition: transform .15s ease, box-shadow .2s ease !important;
    box-shadow: 0 8px 18px rgba(108,99,255,.35);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 24px rgba(108,99,255,.45);
}

.stDownloadButton > button {
    border-radius: 10px !important;
    border: 1px solid rgba(0,212,255,.4) !important;
    background: rgba(0,212,255,.12) !important;
    color: var(--text) !important;
}

.stMultiSelect div[data-baseweb="select"] > div,
.stTextInput div[data-baseweb="base-input"] > div,
.stDateInput div[data-baseweb="input"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}

/* ── Alerts / info ── */
.stAlert {
    border-radius: 12px;
    border: 1px solid var(--border);
}

/* ── Responsive layout ── */
@media (max-width: 1024px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
    .hero {
        padding: 1.2rem 1.2rem;
        border-radius: 14px;
    }
    .hero h1 {
        font-size: 1.6rem;
    }
    .hero p {
        font-size: .9rem;
    }
}

@media (max-width: 768px) {
    .block-container {
        padding-top: .5rem;
        padding-bottom: 5.6rem;
    }
    .kpi-card {
        padding: .85rem .9rem;
    }
    .kpi-value {
        font-size: 1.35rem;
    }
    .section-title {
        font-size: 1rem;
    }
    .stButton > button, .stDownloadButton > button {
        width: 100%;
    }
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    [data-testid="stHorizontalBlock"] {
        gap: .35rem !important;
    }
}

.mobile-bottom-nav {
    display: none;
}

@media (max-width: 768px) {
    .mobile-bottom-nav {
        position: fixed;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 9999;
        background: rgba(11, 16, 32, 0.94);
        border-top: 1px solid rgba(167,179,212,.25);
        backdrop-filter: blur(10px);
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        padding: .35rem .2rem calc(.35rem + env(safe-area-inset-bottom));
        gap: .15rem;
    }
    .mobile-bottom-nav a {
        text-decoration: none;
        color: #A7B3D4;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: .1rem;
        font-size: .64rem;
        padding: .32rem .1rem;
        border-radius: 10px;
        line-height: 1.1;
    }
    .mobile-bottom-nav a .icon {
        font-size: 1rem;
    }
    .mobile-bottom-nav a.active {
        color: #E6ECFF;
        background: rgba(108,99,255,.28);
    }
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>Imprimatur - Dashboard prodaje</h1>
  <p>Izdavačka kuća · Bosna i Hercegovina &nbsp;|&nbsp; Analitika prodajnih kanala</p>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "ai_text" not in st.session_state:
    st.session_state.ai_text = ""
if "last_report_bytes" not in st.session_state:
    st.session_state.last_report_bytes = None
if "last_report_name" not in st.session_state:
    st.session_state.last_report_name = ""
if "ai_report_bytes" not in st.session_state:
    st.session_state.ai_report_bytes = None
if "ai_report_name" not in st.session_state:
    st.session_state.ai_report_name = ""

# ── Helpers ───────────────────────────────────────────────────────────────────
REQUIRED_BASE_COLS = {"Datum", "Naslov", "Autor", "Kolicina", "Cijena", "Zemlja"}
MISSING_KANAL_LABEL = "Nepoznato"
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

def load_csv(uploaded_file, require_kanal: bool = False, default_kanal: str = MISSING_KANAL_LABEL):
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
        required_cols = REQUIRED_BASE_COLS | ({"Kanal"} if require_kanal else set())
        missing = required_cols - set(df.columns)
        if missing:
            st.warning(f"Fajl **{uploaded_file.name}** nedostaju kolone: {', '.join(missing)}")
            return None
        if "Kanal" not in df.columns:
            df["Kanal"] = default_kanal
        df["Kanal"] = df["Kanal"].fillna("").astype(str).str.strip()
        df["Kanal"] = df["Kanal"].replace("", default_kanal)
        df["Datum"] = pd.to_datetime(df["Datum"], dayfirst=True, errors="coerce")
        df["Kolicina"] = pd.to_numeric(df["Kolicina"], errors="coerce").fillna(0).astype(int)
        df["Cijena"] = pd.to_numeric(df["Cijena"], errors="coerce").fillna(0.0)
        df["Prihod"] = df["Kolicina"] * df["Cijena"]
        return df
    except Exception as e:
        st.error(f"Greška pri učitavanju {uploaded_file.name}: {e}")
        return None

def fmt_bam(val):
    return f"{val:,.2f} KM"

CRIMSON = "#8B2635"
CREAM   = "#F5EBE0"
PALETTE = ["#6C63FF", "#00D4FF", "#45D483", "#FFB547", "#FF6B8A",
           "#8D86FF", "#39A0ED", "#A66BFF", "#00C2A8", "#FF8A65"]

def notify(message: str, icon: str | None = None):
    if hasattr(st, "toast"):
        if icon:
            st.toast(message, icon=icon)
        else:
            st.toast(message)

def sanitize_text(value: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in value.strip())
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe.strip("_") or "Izvjestaj"

def save_report(pdf_bytes: bytes, report_label: str) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{sanitize_text(report_label)}_{timestamp}.pdf"
    path = os.path.join(REPORTS_DIR, filename)
    with open(path, "wb") as f:
        f.write(pdf_bytes)
    return filename

def list_reports():
    files = []
    for name in os.listdir(REPORTS_DIR):
        if name.lower().endswith(".pdf"):
            full_path = os.path.join(REPORTS_DIR, name)
            stat = os.stat(full_path)
            files.append({
                "name": name,
                "path": full_path,
                "created": datetime.fromtimestamp(stat.st_mtime).strftime("%d.%m.%Y %H:%M:%S"),
                "size_kb": round(stat.st_size / 1024, 1),
                "timestamp": stat.st_mtime,
            })
    files.sort(key=lambda x: x["timestamp"], reverse=True)
    return files

def estimate_price_km(seed: str) -> float:
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    value = int(digest[:8], 16)
    return round(12 + (value % 3900) / 100, 2)

DUMMY_MARKET_CATALOG = {
    "US": [
        ("Atomic Habits", "James Clear", "Self-help"),
        ("Fourth Wing", "Rebecca Yarros", "Fantasy"),
        ("The Women", "Kristin Hannah", "Drama"),
        ("Yellowface", "R.F. Kuang", "Thriller"),
        ("The Anxious Generation", "Jonathan Haidt", "Psihologija"),
        ("Tomorrow, and Tomorrow, and Tomorrow", "Gabrielle Zevin", "Drama"),
        ("The Midnight Library", "Matt Haig", "Drama"),
        ("The Covenant of Water", "Abraham Verghese", "Drama"),
        ("Demon Copperhead", "Barbara Kingsolver", "Drama"),
        ("The Heaven & Earth Grocery Store", "James McBride", "Drama"),
        ("The Creative Act", "Rick Rubin", "Biznis"),
        ("Sapiens", "Yuval Noah Harari", "Istorija"),
    ],
    "BA": [
        ("Na Drini cuprija", "Ivo Andric", "Klasik"),
        ("Dervis i smrt", "Mesa Selimovic", "Drama"),
        ("Tvrdjava", "Mesa Selimovic", "Drama"),
        ("Legenda o Ali-pasi", "Enes Karic", "Istorija"),
        ("Knjiga o Uni", "Faruk Sehic", "Drama"),
        ("Sarajevski Marlboro", "Miljenko Jergovic", "Drama"),
        ("Gorski vijenac", "Petar II Petrovic Njegos", "Klasik"),
        ("Bosanski lonac", "Adisa Basic", "Kuhar"),
        ("Sin", "Aleksandar Hemon", "Drama"),
        ("Lovac na tijela", "Nenad Velickovic", "Triler"),
    ],
    "RS": [
        ("Knjiga o Milutinu", "Danko Popovic", "Klasik"),
        ("Seobe", "Milos Crnjanski", "Klasik"),
        ("Hazarski recnik", "Milorad Pavic", "Fantastika"),
        ("Koreni", "Dobrica Cosic", "Drama"),
        ("Beskrajni plavi krug", "Branko Copic", "Drama"),
        ("Bas je bezveze", "Marko Vidojkovic", "Humor"),
        ("Prirucnik za samopomoc", "Jelena Bacic Alimpic", "Self-help"),
        ("Cuvam te", "Vesna Dedic", "Drama"),
        ("Deca zla", "Miodrag Majic", "Triler"),
        ("Sva moja radost", "Ljubica Arsic", "Drama"),
    ],
    "HR": [
        ("U registraturi", "Ante Kovacic", "Klasik"),
        ("Ciganin, ali najljepsi", "Kristian Novak", "Drama"),
        ("Sjene na Mjesecu", "Miro Gavran", "Drama"),
        ("Hotel Zagorje", "Ivana Bodrozic", "Drama"),
        ("Sinovi, kceri", "Ivana Bodrozic", "Drama"),
        ("Rikverc", "Jurica Pavicic", "Krimi"),
        ("Noz", "Vedrana Rudan", "Drama"),
        ("Slujkinjina prica", "Margaret Atwood", "Fantastika"),
        ("Nadji me", "Andrej Nikolaidis", "Drama"),
        ("Mirovanje", "Marko Pogacar", "Poezija"),
    ],
}

ALL_BOOK_GENRES = sorted({genre for books in DUMMY_MARKET_CATALOG.values() for _, _, genre in books})

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_trending_books(country_code: str, selected_genres: list[str], max_results: int = 12):
    base = DUMMY_MARKET_CATALOG.get(country_code, DUMMY_MARKET_CATALOG["US"])
    if selected_genres:
        base = [item for item in base if item[2] in selected_genres]

    books = []
    for idx, (title, author, genre) in enumerate(base[:max_results]):
        price = estimate_price_km(f"{country_code}-{title}-{author}")
        books.append({
            "Naslov": title,
            "Autor": author,
            "Zanr": genre,
            "Datum izdanja": str(2018 + (idx % 8)),
            "Dostupnost": "dostupno za nabavku" if idx % 3 != 0 else "nije dostupno za nabavku",
            "Cijena": f"{price:.2f} KM (procjena)",
        })
    return books

def plot_pie(df):
    grp = df.groupby("Kanal")["Prihod"].sum().reset_index()
    fig = px.pie(grp, names="Kanal", values="Prihod",
                 color_discrete_sequence=PALETTE,
                 hole=.55)
    fig.update_traces(
        textposition="outside",
        textinfo="label+percent",
        marker=dict(line=dict(color="#0B1020", width=2)),
        pull=[0.02] * len(grp),
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
    )
    return fig

def plot_top10(df):
    grp = df.groupby("Naslov")["Kolicina"].sum().nlargest(10).reset_index()
    grp = grp.sort_values("Kolicina")
    fig = px.bar(grp, x="Kolicina", y="Naslov", orientation="h",
                 color="Kolicina", color_continuous_scale="Bluered")
    fig.update_traces(
        marker_line_width=0,
        opacity=0.9,
        text=grp["Kolicina"],
        textposition="outside",
        texttemplate="%{text:,.0f}",
        cliponaxis=False,
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        yaxis_title=None,
        xaxis_title="Prodano primjeraka",
        margin=dict(t=10, b=10, l=10, r=60),
        coloraxis_showscale=False,
    )
    fig.update_yaxes(tickfont_size=11, gridcolor="rgba(167,179,212,0.15)")
    fig.update_xaxes(gridcolor="rgba(167,179,212,0.15)")
    return fig

def plot_zemlja(df):
    grp = df.groupby("Zemlja")["Prihod"].sum().reset_index()
    fig = px.bar(grp, x="Zemlja", y="Prihod",
                 color="Prihod", color_continuous_scale="Viridis")
    fig.update_traces(marker_line_width=0, opacity=0.92)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_family="Inter",
        yaxis_title="Prihod (KM)",
        xaxis_title=None,
        margin=dict(t=10, b=10, l=10, r=10),
        coloraxis_showscale=False,
    )
    fig.update_yaxes(gridcolor="rgba(167,179,212,0.15)")
    return fig

def build_summary(df) -> str:
    total_prihod = df["Prihod"].sum()
    total_kom = df["Kolicina"].sum()
    naslovi = df["Naslov"].nunique()

    po_kanalu = df.groupby("Kanal").agg(Prihod=("Prihod","sum"), Kolicina=("Kolicina","sum")).to_string()
    top5 = df.groupby("Naslov")["Kolicina"].sum().nlargest(5).to_string()
    po_zemlji = df.groupby("Zemlja").agg(Prihod=("Prihod","sum"), Kolicina=("Kolicina","sum")).to_string()

    return f"""
Izvještaj prodaje — Imprimatur (BiH)
Datum analize: {datetime.now().strftime('%d.%m.%Y.')}

UKUPNI KPI:
- Ukupan prihod: {fmt_bam(total_prihod)}
- Prodano primjeraka: {total_kom:,}
- Broj naslova: {naslovi}

PRODAJA PO KANALIMA:
{po_kanalu}

TOP 5 NASLOVA (po količini):
{top5}

PRODAJA PO ZEMLJAMA:
{po_zemlji}
""".strip()

def generate_pdf(df, ai_text: str) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    crimson = colors.HexColor("#8B2635")
    cream   = colors.HexColor("#F5EBE0")

    title_style = ParagraphStyle("Title", parent=styles["Title"],
                                  fontName="Helvetica-Bold", fontSize=20,
                                  textColor=crimson, alignment=TA_CENTER, spaceAfter=6)
    sub_style   = ParagraphStyle("Sub", parent=styles["Normal"],
                                  fontName="Helvetica", fontSize=10,
                                  textColor=colors.HexColor("#7A6355"),
                                  alignment=TA_CENTER, spaceAfter=16)
    h2_style    = ParagraphStyle("H2", parent=styles["Heading2"],
                                  fontName="Helvetica-Bold", fontSize=13,
                                  textColor=crimson, spaceBefore=14, spaceAfter=6)
    body_style  = ParagraphStyle("Body", parent=styles["Normal"],
                                  fontName="Helvetica", fontSize=10, leading=15)

    story = []
    story.append(Paragraph("Imprimatur — Dashboard prodaje", title_style))
    story.append(Paragraph(f"Generisano: {datetime.now().strftime('%d.%m.%Y. %H:%M')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=crimson, spaceAfter=12))

    # KPIs
    story.append(Paragraph("Ključni pokazatelji", h2_style))
    kpi_data = [
        ["Ukupan prihod", fmt_bam(df["Prihod"].sum())],
        ["Prodano primjeraka", f"{df['Kolicina'].sum():,}"],
        ["Broj naslova", str(df["Naslov"].nunique())],
    ]
    tbl = Table(kpi_data, colWidths=[8*cm, 8*cm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,-1), cream),
        ("TEXTCOLOR",  (0,0),(0,-1),  colors.HexColor("#7A6355")),
        ("TEXTCOLOR",  (1,0),(1,-1),  crimson),
        ("FONTNAME",   (0,0),(-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,0),(-1,-1), 10),
        ("FONTNAME",   (1,0),(1,-1),  "Helvetica-Bold"),
        ("FONTSIZE",   (1,0),(1,-1),  12),
        ("ROWBACKGROUNDS", (0,0),(-1,-1), [cream, colors.white]),
        ("GRID",       (0,0),(-1,-1), .5, colors.HexColor("#EAD5C0")),
        ("PADDING",    (0,0),(-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 12))

    # Top naslovi
    story.append(Paragraph("Top 10 naslova po količini", h2_style))
    top10 = df.groupby("Naslov")["Kolicina"].sum().nlargest(10).reset_index()
    top10.columns = ["Naslov", "Prodano"]
    t_data = [["Naslov", "Prodano primjeraka"]] + top10.values.tolist()
    t = Table(t_data, colWidths=[12*cm, 4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0),  crimson),
        ("TEXTCOLOR",  (0,0),(-1,0),  colors.white),
        ("FONTNAME",   (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.white, cream]),
        ("GRID",       (0,0),(-1,-1), .4, colors.HexColor("#EAD5C0")),
        ("PADDING",    (0,0),(-1,-1), 6),
        ("ALIGN",      (1,0),(1,-1),  "CENTER"),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Prihod po kanalu
    story.append(Paragraph("Prihod po kanalu distribucije", h2_style))
    kanal = df.groupby("Kanal").agg(Prihod=("Prihod","sum"), Kolicina=("Kolicina","sum")).reset_index()
    k_data = [["Kanal", "Prihod (KM)", "Količina"]]
    for _, row in kanal.iterrows():
        k_data.append([row["Kanal"], fmt_bam(row["Prihod"]), str(int(row["Kolicina"]))])
    kt = Table(k_data, colWidths=[6*cm, 6*cm, 4*cm])
    kt.setStyle(TableStyle([
        ("BACKGROUND", (0,0),(-1,0),  crimson),
        ("TEXTCOLOR",  (0,0),(-1,0),  colors.white),
        ("FONTNAME",   (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",   (0,0),(-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [colors.white, cream]),
        ("GRID",       (0,0),(-1,-1), .4, colors.HexColor("#EAD5C0")),
        ("PADDING",    (0,0),(-1,-1), 6),
        ("ALIGN",      (1,0),(-1,-1), "CENTER"),
    ]))
    story.append(kt)
    story.append(Spacer(1, 12))

    # AI preporuke
    if ai_text:
        story.append(HRFlowable(width="100%", thickness=1, color=crimson, spaceAfter=8))
        story.append(Paragraph("AI Preporuke (Claude)", h2_style))
        for line in ai_text.split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), body_style))
                story.append(Spacer(1, 3))

    doc.build(story)
    return buf.getvalue()

# ── Sidebar navigation ────────────────────────────────────────────────────────
PAGES = ["Pocetna", "Pregled", "AI Preporuke", "Trending", "Izvjestaji"]
if "page" not in st.session_state:
    st.session_state.page = PAGES[0]

requested_page = st.query_params.get("page")
if isinstance(requested_page, list):
    requested_page = requested_page[0] if requested_page else None
if requested_page in PAGES:
    st.session_state.page = requested_page

with st.sidebar:
    st.markdown("### Navigacija")
    st.markdown("Kontrolni centar aplikacije")
    sidebar_page = st.radio(
        "Izaberite ekran",
        PAGES,
        index=PAGES.index(st.session_state.page),
        label_visibility="collapsed",
    )
    if sidebar_page != st.session_state.page:
        st.session_state.page = sidebar_page

st.query_params["page"] = st.session_state.page

page = st.session_state.page

mobile_nav_items = [
    ("Pocetna", "📥"),
    ("Pregled", "📊"),
    ("AI Preporuke", "🤖"),
    ("Trending", "🔥"),
    ("Izvjestaji", "🧾"),
]
mobile_nav_html = '<nav class="mobile-bottom-nav">'
for label, icon in mobile_nav_items:
    active_class = "active" if page == label else ""
    href_page = label.replace(" ", "%20")
    mobile_nav_html += (
        f'<a class="{active_class}" href="?page={href_page}">'
        f'<span class="icon">{icon}</span><span>{label}</span></a>'
    )
mobile_nav_html += "</nav>"
st.markdown(mobile_nav_html, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Upload & Consolidate
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Pocetna":
    st.markdown('<p class="section-title">Učitavanje podataka</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="upload-hint">
    Svaki CSV fajl treba sadržavati kolone: 
    <strong>Datum, Naslov, Autor, Kolicina, Cijena, Zemlja</strong><br>
    Kolona <strong>Kanal</strong> je opcionalna za dokumente iz izvora ispod.<br>
    Za detaljan pregled po kanalima možete uploadovati poseban fajl koji već sadrži kolonu <strong>Kanal</strong>.<br>
    Podržani formati datuma: DD.MM.YYYY ili YYYY-MM-DD
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        f_knjizare = st.file_uploader("Prodaja iz knjizara", type="csv", key="knjizare")
    with col2:
        f_webshop  = st.file_uploader("Web shop",              type="csv", key="webshop")
    with col3:
        f_sajmovi  = st.file_uploader("Sajmovi",               type="csv", key="sajmovi")
    with col4:
        f_kanali   = st.file_uploader("Fajl sa kolonom Kanal", type="csv", key="kanali")

    if st.button("Pregled"):
        frames = []
        source_files = [
            (f_knjizare, "Knjizara", False),
            (f_webshop, "Web shop", False),
            (f_sajmovi, "Sajam", False),
            (f_kanali, MISSING_KANAL_LABEL, True),
        ]
        for f, default_kanal, require_kanal in source_files:
            if f:
                df_tmp = load_csv(f, require_kanal=require_kanal, default_kanal=default_kanal)
                if df_tmp is not None:
                    frames.append(df_tmp)
        if not frames:
            st.error("Uploadujte barem jedan validan CSV fajl.")
        else:
            combined = pd.concat(frames, ignore_index=True)
            st.session_state.df = combined
            st.session_state.ai_text = ""
            st.success(f"Konsolidovano **{len(combined):,}** redova iz **{len(frames)}** izvora.")
            notify(f"Uspješno konsolidovano {len(combined):,} redova.")

    # Preview
    if st.session_state.df is not None:
        df = st.session_state.df
        st.markdown('<p class="section-title">Pregled konsolidovanog DataFrame-a</p>', unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Ukupno redova", f"{len(df):,}")
        c2.metric("Naslova", df["Naslov"].nunique())
        c3.metric("Kanala", df["Kanal"].nunique())
        c4.metric("Zemalja", df["Zemlja"].nunique())

        st.dataframe(df.head(50), use_container_width=True, height=320)

        # Sample CSV download helper
        st.markdown('<p class="section-title">Primjer CSV-a za testiranje</p>', unsafe_allow_html=True)
        sample = pd.DataFrame({
            "Datum":   ["01.01.2025","15.01.2025","20.02.2025","10.03.2025","25.03.2025"],
            "Naslov":  ["Bosanska hronika","Gorski vijenac","Derviš i smrt","Prokleta avlija","Na Drini ćuprija"],
            "Autor":   ["Ivo Andrić","Petar II","Mesa Selimović","Ivo Andrić","Ivo Andrić"],
            "Kolicina":[12, 8, 15, 6, 20],
            "Cijena":  [18.50, 14.00, 19.90, 16.50, 22.00],
            "Kanal":   ["Knjizara","Web shop","Knjizara","Sajam","Web shop"],
            "Zemlja":  ["BiH","Srbija","BiH","Hrvatska","BiH"],
        })
        csv_bytes = sample.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button("Preuzmi primjer CSV-a", csv_bytes, "primjer_prodaja.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Pregled":
    if st.session_state.df is None:
        st.info("Najprije uploadujte i konsolidujte podatke u meniju **Pocetna**.")
    else:
        df = st.session_state.df

        # ── Filters ──────────────────────────────────────────────────────────
        with st.expander("Filtri", expanded=False):
            fc1, fc2, fc3 = st.columns(3)
            selected_kanal = fc1.multiselect("Kanal", df["Kanal"].unique(), default=list(df["Kanal"].unique()))
            selected_zemlja = fc2.multiselect("Zemlja", df["Zemlja"].unique(), default=list(df["Zemlja"].unique()))
            authors = sorted(df["Autor"].dropna().unique())
            selected_autor = fc3.multiselect("Autor", authors, default=authors)

        mask = (
            df["Kanal"].isin(selected_kanal) &
            df["Zemlja"].isin(selected_zemlja) &
            df["Autor"].isin(selected_autor)
        )
        dff = df[mask]

        # ── KPIs ─────────────────────────────────────────────────────────────
        st.markdown('<p class="section-title">Ključni pokazatelji</p>', unsafe_allow_html=True)
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Ukupan prihod</div><div class="kpi-value">{fmt_bam(dff["Prihod"].sum())}</div></div>', unsafe_allow_html=True)
        with k2:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Prodano primjeraka</div><div class="kpi-value">{dff["Kolicina"].sum():,}</div></div>', unsafe_allow_html=True)
        with k3:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Unikatnih naslova</div><div class="kpi-value">{dff["Naslov"].nunique()}</div></div>', unsafe_allow_html=True)
        with k4:
            avg = dff["Cijena"].mean() if len(dff) else 0
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Prosj. cijena</div><div class="kpi-value">{avg:.2f} KM</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Charts row 1 ────────────────────────────────────────────────────
        st.markdown('<p class="section-title">Grafički prikaz</p>', unsafe_allow_html=True)
        ch1, ch2 = st.columns([1, 1.6])
        with ch1:
            st.markdown("**Prihod po kanalima**")
            st.plotly_chart(plot_pie(dff), use_container_width=True)
        with ch2:
            st.markdown("**Top 10 naslova po količini**")
            st.plotly_chart(plot_top10(dff), use_container_width=True)

        # ── Charts row 2 ────────────────────────────────────────────────────
        st.markdown("**Prihod po zemljama**")
        st.plotly_chart(plot_zemlja(dff), use_container_width=True)

        # ── Detail table ─────────────────────────────────────────────────────
        st.markdown('<p class="section-title">Detalji po naslovu, kanalu i zemlji</p>', unsafe_allow_html=True)
        detail = (
            dff.groupby(["Naslov","Autor","Kanal","Zemlja"])
            .agg(Kolicina=("Kolicina","sum"), Prihod=("Prihod","sum"))
            .reset_index()
            .sort_values("Prihod", ascending=False)
        )
        detail["Prihod (KM)"] = detail["Prihod"].apply(lambda x: f"{x:,.2f}")
        st.dataframe(
            detail.drop(columns="Prihod"),
            use_container_width=True,
            height=380,
            hide_index=True,
        )

        # ── PDF Export ───────────────────────────────────────────────────────
        st.markdown('<p class="section-title">Export</p>', unsafe_allow_html=True)
        if st.button("Generisi PDF izvjestaj"):
            with st.spinner("Pripremam PDF…"):
                pdf_bytes = generate_pdf(dff, st.session_state.ai_text)
                if len(selected_kanal) == 1:
                    report_scope = selected_kanal[0]
                elif len(selected_kanal) > 1:
                    report_scope = "Kombinovano"
                else:
                    report_scope = "PrazanFilter"
                report_name = save_report(pdf_bytes, f"Izvjestaj_{report_scope}")
                st.session_state.last_report_bytes = pdf_bytes
                st.session_state.last_report_name = report_name
                notify(f"Izvjestaj sacuvan lokalno: {report_name}")
            st.download_button(
                "Preuzmi PDF",
                st.session_state.last_report_bytes,
                st.session_state.last_report_name,
                "application/pdf",
            )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — AI Recommendations
# ═══════════════════════════════════════════════════════════════════════════════
if page == "AI Preporuke":
    if st.session_state.df is None:
        st.info("Najprije uploadujte i konsolidujte podatke u meniju **Pocetna**.")
    else:
        df = st.session_state.df
        st.markdown('<p class="section-title">AI analiza prodaje</p>', unsafe_allow_html=True)
        st.markdown("""
        Claude analizira vaše prodajne podatke i daje konkretne preporuke:
        koji naslov marketirati gdje, koji kanal pojačati i koji tržišni fokus razvijati.
        """)

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            api_key = st.text_input("Unesite Anthropic API ključ", type="password",
                                    placeholder="sk-ant-...")

        if st.button("Generisi AI preporuke"):
            if not api_key:
                st.error("API ključ je obavezan.")
            else:
                summary = build_summary(df)
                prompt = f"""Ti si ekspert za marketinšku analitiku u knjižarskoj industriji na prostoru bivše Jugoslavije (BiH, Srbija, Hrvatska).

Analiziraj sljedeće prodajne podatke izdavačke kuće Imprimatur iz Bosne i Hercegovine:

{summary}

Na osnovu podataka daj strukturirane preporuke u tri sekcije:

1. **MARKETING NASLOVA** — Za svaki od top 5 naslova preporuči specifičan marketing pristup u kojoj zemlji i zašto.

2. **OPTIMIZACIJA KANALA** — Koji prodajni kanal ima najveći potencijal rasta? Koje konkretne mjere predlažeš?

3. **STRATEŠKI FOKUS** — Preporuči 2-3 strateška koraka: kombinaciju tržište + naslov + kanal koji obećava najviše rasta.

Budi konkretan, koristi brojeve iz podataka i daj akcione preporuke. Odgovori na bosanskom/srpsko-hrvatskom jeziku."""

                with st.spinner("Claude analizira podatke…"):
                    try:
                        client = Anthropic(api_key=api_key)
                        response = client.messages.create(
                            model="claude-sonnet-4-5",
                            max_tokens=1500,
                            messages=[{"role": "user", "content": prompt}],
                        )
                        ai_result = response.content[0].text
                        st.session_state.ai_text = ai_result
                        ai_pdf = generate_pdf(df, ai_result)
                        st.session_state.ai_report_bytes = ai_pdf
                        st.session_state.ai_report_name = save_report(ai_pdf, "Izvjestaj_AI_Preporuke")
                        notify(f"AI izvjestaj sacuvan lokalno: {st.session_state.ai_report_name}")
                        notify("AI preporuke su spremne.")
                    except Exception as e:
                        st.error(f"Greška pri pozivu API-ja: {e}")
                        ai_result = None

        if st.session_state.ai_text:
            st.markdown(f'<div class="ai-box">{st.session_state.ai_text}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                "Preuzmi PDF sa AI preporukama",
                st.session_state.ai_report_bytes,
                st.session_state.ai_report_name,
                "application/pdf",
            )

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Trending Books
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Trending":
    st.markdown('<p class="section-title">Trending knjiga i trzista</p>', unsafe_allow_html=True)
    st.markdown(
        "Testni podaci se ucitavaju iz lokalnog dummy izvora za globalni pregled i trzista na kojima poslujete."
    )

    c1, c2 = st.columns([1.5, 1])
    selected_genres = c1.multiselect(
        "Zanr",
        options=ALL_BOOK_GENRES,
        default=[],
        placeholder="Izaberite zanr (prazno = svi)",
    )
    max_items = c2.number_input(
        "Broj rezultata po trzistu",
        min_value=1,
        max_value=30,
        value=10,
        step=1,
    )

    markets = {
        "Globalno": "US",
        "Bosna i Hercegovina": "BA",
        "Srbija": "RS",
        "Hrvatska": "HR",
    }

    if st.button("Ucitaj trendove", use_container_width=True):
        for label, code in markets.items():
            try:
                records = fetch_trending_books(code, selected_genres, max_results=max_items)
                st.markdown(f"#### {label}")
                if records:
                    st.dataframe(pd.DataFrame(records), use_container_width=True, hide_index=True, height=320)
                else:
                    st.info(f"Nema dostupnih podataka za: {label}")
            except Exception as e:
                st.warning(f"Neuspjelo ucitavanje za {label}: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — Saved Reports
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Izvjestaji":
    st.markdown('<p class="section-title">Sacuvani izvjestaji</p>', unsafe_allow_html=True)
    reports = list_reports()

    if not reports:
        st.info("Nema sacuvanih izvjestaja.")
    else:
        default_start = datetime.fromtimestamp(reports[-1]["timestamp"]).date()
        default_end = datetime.fromtimestamp(reports[0]["timestamp"]).date()
        f1, f2, f3 = st.columns([1.1, 1.1, 1.2])
        start_date = f1.date_input("Od datuma", value=default_start)
        end_date = f2.date_input("Do datuma", value=default_end)
        sort_order = f3.selectbox("Sortiranje", ["Najnoviji prvo", "Najstariji prvo"], index=0)

        filtered_reports = []
        for report in reports:
            report_date = datetime.fromtimestamp(report["timestamp"]).date()
            if start_date <= report_date <= end_date:
                filtered_reports.append(report)

        reverse_sort = sort_order == "Najnoviji prvo"
        filtered_reports = sorted(filtered_reports, key=lambda x: x["timestamp"], reverse=reverse_sort)

        if not filtered_reports:
            st.warning("Nema izvjestaja za izabrani vremenski opseg.")
        else:
            h1, h2, h3, h4 = st.columns([4.2, 2.2, 1.2, 1.6])
            h1.markdown("**Naziv**")
            h2.markdown("**Datum i vrijeme**")
            h3.markdown("**Velicina (KB)**")
            h4.markdown("**Akcija**")

            for idx, report in enumerate(filtered_reports):
                c1, c2, c3, c4 = st.columns([4.2, 2.2, 1.2, 1.6])
                c1.write(report["name"])
                c2.write(report["created"])
                c3.write(report["size_kb"])
                with open(report["path"], "rb") as f:
                    pdf_data = f.read()
                c4.download_button(
                    "Preuzmi",
                    data=pdf_data,
                    file_name=report["name"],
                    mime="application/pdf",
                    key=f"download_report_{idx}_{report['name']}",
                    use_container_width=True,
                )
