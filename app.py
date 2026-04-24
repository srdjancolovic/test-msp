import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from anthropic import Anthropic
import io
import os
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
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700;900&family=Source+Sans+3:wght@300;400;600&display=swap');

:root {
    --crimson:   #8B2635;
    --crimson-dk:#6A1B27;
    --crimson-lt:#B03A4D;
    --cream:     #F5EBE0;
    --cream-dk:  #EAD5C0;
    --ink:       #1C1008;
    --muted:     #7A6355;
    --white:     #FDFAF7;
}

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    background-color: var(--cream);
    color: var(--ink);
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 2rem; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, var(--crimson-dk) 0%, var(--crimson) 60%, var(--crimson-lt) 100%);
    border-radius: 4px;
    padding: 2.2rem 2.8rem;
    margin-bottom: 1.6rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: "📚";
    position: absolute;
    right: 2rem; top: 50%;
    transform: translateY(-50%);
    font-size: 6rem;
    opacity: .12;
}
.hero h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 900;
    color: var(--cream) !important;
    margin: 0 0 .3rem 0;
    letter-spacing: .02em;
}
.hero p {
    color: var(--cream-dk);
    font-size: 1rem;
    margin: 0;
    font-weight: 300;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 2px solid var(--crimson);
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 600;
    font-size: .95rem;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: var(--muted);
    padding: .7rem 1.6rem;
    background: transparent;
    border: none;
    border-bottom: 3px solid transparent;
    margin-bottom: -2px;
    transition: color .2s, border-color .2s;
}
.stTabs [aria-selected="true"] {
    color: var(--crimson) !important;
    border-bottom-color: var(--crimson) !important;
    background: transparent !important;
}

/* ── KPI cards ── */
.kpi-card {
    background: var(--white);
    border-left: 4px solid var(--crimson);
    border-radius: 3px;
    padding: 1.1rem 1.4rem;
    box-shadow: 0 2px 8px rgba(139,38,53,.08);
}
.kpi-label {
    font-size: .78rem;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: .3rem;
}
.kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--crimson-dk);
    line-height: 1;
}

/* ── Section headers ── */
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--crimson-dk);
    border-bottom: 1px solid var(--cream-dk);
    padding-bottom: .45rem;
    margin: 1.4rem 0 .9rem 0;
}

/* ── Upload area ── */
.upload-hint {
    background: var(--white);
    border: 2px dashed var(--cream-dk);
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    font-size: .9rem;
    color: var(--muted);
    margin-bottom: .8rem;
}

/* ── AI box ── */
.ai-box {
    background: var(--white);
    border-left: 4px solid var(--crimson);
    border-radius: 3px;
    padding: 1.4rem 1.7rem;
    box-shadow: 0 2px 12px rgba(139,38,53,.1);
    white-space: pre-wrap;
    font-size: .95rem;
    line-height: 1.7;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--crimson) !important;
    color: var(--cream) !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: .07em !important;
    text-transform: uppercase !important;
    font-size: .85rem !important;
    border: none !important;
    border-radius: 3px !important;
    padding: .6rem 1.8rem !important;
    transition: background .2s !important;
}
.stButton > button:hover {
    background: var(--crimson-dk) !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: 4px; overflow: hidden; }

/* ── Alerts / info ── */
.stAlert { border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>📚 Imprimatur — Dashboard prodaje</h1>
  <p>Izdavačka kuća · Bosna i Hercegovina &nbsp;|&nbsp; Analitika prodajnih kanala</p>
</div>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "df" not in st.session_state:
    st.session_state.df = None
if "ai_text" not in st.session_state:
    st.session_state.ai_text = ""

# ── Helpers ───────────────────────────────────────────────────────────────────
REQUIRED_BASE_COLS = {"Datum", "Naslov", "Autor", "Kolicina", "Cijena", "Zemlja"}
MISSING_KANAL_LABEL = "Nepoznato"

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
PALETTE = ["#8B2635","#B03A4D","#C96070","#D4909A","#E8C0C6",
           "#6A1B27","#F5EBE0","#A0522D","#CD853F","#DEB887"]

def plot_pie(df):
    grp = df.groupby("Kanal")["Prihod"].sum().reset_index()
    fig = px.pie(grp, names="Kanal", values="Prihod",
                 color_discrete_sequence=PALETTE,
                 hole=.38)
    fig.update_traces(textposition="outside", textinfo="label+percent",
                      marker=dict(line=dict(color=CREAM, width=2)))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_family="Source Sans 3", showlegend=False,
                      margin=dict(t=20,b=20,l=20,r=20))
    return fig

def plot_top10(df):
    grp = df.groupby("Naslov")["Kolicina"].sum().nlargest(10).reset_index()
    grp = grp.sort_values("Kolicina")
    fig = px.bar(grp, x="Kolicina", y="Naslov", orientation="h",
                 color_discrete_sequence=[CRIMSON])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_family="Source Sans 3", yaxis_title=None, xaxis_title="Prodano primjeraka",
                      margin=dict(t=10,b=10,l=10,r=10))
    fig.update_yaxes(tickfont_size=11)
    return fig

def plot_zemlja(df):
    grp = df.groupby("Zemlja")["Prihod"].sum().reset_index()
    fig = px.bar(grp, x="Zemlja", y="Prihod",
                 color_discrete_sequence=[CRIMSON,"#B03A4D","#6A1B27"])
    fig.update_traces(marker_line_width=0)
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font_family="Source Sans 3", yaxis_title="Prihod (KM)", xaxis_title=None,
                      margin=dict(t=10,b=10,l=10,r=10))
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
    story.append(Paragraph("📚 Imprimatur — Dashboard prodaje", title_style))
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

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📂  Konsolidacija", "📊  Pregled", "🤖  AI Preporuke"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Upload & Consolidate
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
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
        f_knjizare = st.file_uploader("🏪 Prodaja iz knjižara", type="csv", key="knjizare")
    with col2:
        f_webshop  = st.file_uploader("🌐 Web shop",            type="csv", key="webshop")
    with col3:
        f_sajmovi  = st.file_uploader("🎪 Sajmovi",             type="csv", key="sajmovi")
    with col4:
        f_kanali   = st.file_uploader("📊 Fajl sa kolonom Kanal", type="csv", key="kanali")

    if st.button("⚙️  Konsoliduj podatke"):
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
            st.success(f"✅ Konsolidovano **{len(combined):,}** redova iz **{len(frames)}** izvora.")

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
        st.download_button("📥 Preuzmi primjer CSV-a", csv_bytes, "primjer_prodaja.csv", "text/csv")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    if st.session_state.df is None:
        st.info("⬅️ Najprije uploadujte i konsolidujte podatke u tabu **Konsolidacija**.")
    else:
        df = st.session_state.df

        # ── Filters ──────────────────────────────────────────────────────────
        with st.expander("🔍 Filtri", expanded=False):
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
        st.dataframe(detail.drop(columns="Prihod"), use_container_width=True, height=380)

        # ── PDF Export ───────────────────────────────────────────────────────
        st.markdown('<p class="section-title">Export</p>', unsafe_allow_html=True)
        if st.button("📄 Generiši PDF izvještaj"):
            with st.spinner("Pripremam PDF…"):
                pdf_bytes = generate_pdf(dff, st.session_state.ai_text)
            st.download_button(
                "⬇️ Preuzmi PDF",
                pdf_bytes,
                f"imprimatur_izvjestaj_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                "application/pdf",
            )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI Recommendations
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    if st.session_state.df is None:
        st.info("⬅️ Najprije uploadujte i konsolidujte podatke u tabu **Konsolidacija**.")
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
                                    placeholder="sk-ant-…")

        if st.button("🤖 Generiši AI preporuke"):
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
                    except Exception as e:
                        st.error(f"Greška pri pozivu API-ja: {e}")
                        ai_result = None

        if st.session_state.ai_text:
            st.markdown(f'<div class="ai-box">{st.session_state.ai_text}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            pdf_bytes = generate_pdf(df, st.session_state.ai_text)
            st.download_button(
                "📄 Preuzmi PDF sa AI preporukama",
                pdf_bytes,
                f"imprimatur_ai_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                "application/pdf",
            )
