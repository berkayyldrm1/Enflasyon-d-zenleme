# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib requests PyGithub

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
import time
import json
from github import Github
from io import BytesIO
import zipfile
import base64
import requests
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from streamlit_lottie import st_lottie

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded"
)

# --- CSS MOTORU ---
def apply_theme():
    if 'plotly_template' not in st.session_state:
        st.session_state.plotly_template = "plotly_dark"

    final_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

        :root {{
            --bg-deep: #02040a;
            --glass-bg: rgba(255, 255, 255, 0.02);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-main: #f4f4f5;
            --text-dim: #a1a1aa;
            --accent-blue: #3b82f6;
            --card-radius: 16px;
        }}

        .block-container {{
            padding-top: 1rem !important; 
            padding-bottom: 3rem !important;
        }}
        
        header {{visibility: hidden;}}
        [data-testid="stHeader"] {{ visibility: hidden; height: 0px; }}
        [data-testid="stToolbar"] {{ display: none; }}

        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 3px),
                radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 2px);
            background-size: 550px 550px, 350px 350px;
            background-position: 0 0, 40 60;
            opacity: 0.07; z-index: 0; pointer-events: none;
        }}
        
        [data-testid="stAppViewContainer"] {{
            background-color: var(--bg-deep);
            background-image: radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.06), transparent 25%), radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.06), transparent 25%);
            background-attachment: fixed; font-family: 'Inter', sans-serif !important; color: var(--text-main) !important;
        }}
        
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(5, 5, 10, 0.95) 0%, rgba(0, 0, 0, 0.98) 100%) !important;
            border-right: 1px solid var(--glass-border); backdrop-filter: blur(20px); z-index: 99;
        }}
        
        /* RADYO BUTONU MENÜ STİLİ (TAK DİYE GEÇİŞ İÇİN) */
        [data-testid="stRadio"] > div {{
            background-color: transparent;
            border: none;
            padding: 0;
            gap: 8px;
        }}

        [data-testid="stRadio"] label {{
            background-color: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 12px 16px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
            color: #a1a1aa !important;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            display: flex;
            align-items: center;
            width: 100%;
        }}

        [data-testid="stRadio"] label:hover {{
            background-color: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.2);
            color: #fff !important;
            transform: translateX(5px);
        }}

        [data-testid="stRadio"] label[data-checked="true"] {{
            background: linear-gradient(90deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.05) 100%);
            border: 1px solid #3b82f6;
            color: #60a5fa !important;
            font-weight: 700;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.15);
        }}
        
        /* Radyo Yuvarlağını Gizle */
        [data-testid="stRadio"] div[role="radiogroup"] > :first-child {{
            display: none;
        }}

        /* Diğer Bileşenler */
        .kpi-card {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
            border: 1px solid var(--glass-border); border-radius: var(--card-radius);
            padding: 20px; position: relative; overflow: hidden; backdrop-filter: blur(10px);
            z-index: 1; margin-bottom: 20px;
        }}
        .kpi-title {{ font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); letter-spacing: 1px; margin-bottom: 8px; }}
        .kpi-value {{ font-size: 32px; font-weight: 700; color: #fff; margin-bottom: 5px; letter-spacing: -1px; }}
        .kpi-sub {{ font-size: 11px; font-weight: 500; display: flex; align-items: center; gap: 6px; color: var(--text-dim); background: rgba(0,0,0,0.2); padding: 3px 6px; border-radius: 4px; width: fit-content; }}

        .ticker-wrap {{ width: 100%; overflow: hidden; background: rgba(0,0,0,0.2); border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border); padding: 8px 0; margin-bottom: 20px; white-space: nowrap; }}
        .ticker-move {{ display: inline-block; padding-left: 100%; animation: marquee 45s linear infinite; font-family: 'JetBrains Mono', monospace; font-size: 11px; }}
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}

        .smart-card {{ background: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 4px; }}
        .sc-title {{ font-size: 10px; color: #a1a1aa; font-weight:600; text-transform:uppercase; }}
        .sc-val {{ font-size: 18px; color: #fff; font-weight:700; }}
        
        .pg-card {{
            background: rgba(20, 20, 25, 0.4); border: 1px solid var(--glass-border); border-radius: 12px;
            padding: 12px; height: 140px; display: flex; flex-direction: column; justify-content: space-between; align-items: center;
            text-align: center; position: relative; z-index: 1;
        }}
        .pg-name {{ font-size: 12px; font-weight: 500; color: #d4d4d8; line-height: 1.2; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
        .pg-price {{ font-size: 16px; font-weight: 700; color: #fff; margin: 6px 0; }}
        .pg-badge {{ padding: 2px 8px; border-radius: 99px; font-size: 10px; font-weight: 700; }}
        .pg-red {{ background: rgba(239, 68, 68, 0.1); color: #fca5a5; }}
        .pg-green {{ background: rgba(16, 185, 129, 0.1); color: #6ee7b7; }}
        .pg-yellow {{ background: rgba(255, 255, 255, 0.05); color: #ffd966; }}
        
        div.stButton > button {{
            background: linear-gradient(145deg, rgba(40,40,45,0.8), rgba(20,20,25,0.9)); border: 1px solid var(--glass-border);
            color: #fff; border-radius: 10px; font-weight: 600; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        div.stButton > button:hover {{ border-color: var(--accent-blue); box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); transform: translateY(-1px); }}
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# --- 3. RAPOR MOTORU ---
def create_word_report(text_content, tarih, df_analiz=None):
    try:
        doc = Document()
        matplotlib.use('Agg')
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
        head = doc.add_heading(f'PİYASA GÖRÜNÜM RAPORU', 0)
        head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        subhead = doc.add_paragraph(f'Rapor Tarihi: {tarih}')
        subhead.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph("")
        paragraphs = text_content.split('\n')
        for p_text in paragraphs:
            if not p_text.strip(): continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            parts = p_text.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 == 1: 
                    run.bold = True
                    run.font.color.rgb = RGBColor(0, 50, 100) 
        if df_analiz is not None and not df_analiz.empty:
            doc.add_page_break()
            doc.add_heading('EKLER: GÖRSEL ANALİZLER', 1)
            doc.add_paragraph("")
            try:
                if 'Fark' in df_analiz.columns:
                    data = pd.to_numeric(df_analiz['Fark'], errors='coerce').dropna() * 100
                    if not data.empty:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        ax.hist(data, bins=20, color='#3b82f6', edgecolor='white', alpha=0.7)
                        ax.set_title(f"Fiyat Değişim Dağılımı (%) - {tarih}", fontsize=12, fontweight='bold')
                        memfile = BytesIO()
                        plt.savefig(memfile, format='png', dpi=100)
                        plt.close(fig)
                        doc.add_picture(memfile, width=Inches(5.5))
                        memfile.close()
                        doc.add_paragraph("Grafik 1: Ürünlerin fiyat değişim oranlarına göre dağılımı.")
            except Exception:
                pass
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        return BytesIO()

# --- 4. GITHUB İŞLEMLERİ ---
@st.cache_resource
def get_github_connection():
    try:
        return Github(st.secrets["github"]["token"])
    except:
        return None

def get_github_repo():
    g = get_github_connection()
    if g:
        return g.get_repo(st.secrets["github"]["repo_name"])
    return None

@st.cache_data(ttl=600, show_spinner=False)
def github_excel_oku(dosya_adi, sayfa_adi=None):
    repo = get_github_repo()
    if not repo: return pd.DataFrame()
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        if sayfa_adi:
            df = pd.read_excel(BytesIO(c.decoded_content), sheet_name=sayfa_adi, dtype=str)
        else:
            df = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
        return df
    except:
        return pd.DataFrame()

def github_excel_guncelle(df_yeni, dosya_adi):
    repo = get_github_repo()
    if not repo: return "Repo Yok"
    try:
        try:
            c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
            old = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
            yeni_tarih = str(df_yeni['Tarih'].iloc[0])
            old = old[~((old['Tarih'].astype(str) == yeni_tarih) & (old['Kod'].isin(df_yeni['Kod'])))]
            final = pd.concat([old, df_yeni], ignore_index=True)
        except:
            c = None; final = df_yeni
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w:
            final.to_excel(w, index=False, sheet_name='Fiyat_Log')
        msg = f"Data Update"
        if c:
            repo.update_file(c.path, msg, out.getvalue(), c.sha, branch=st.secrets["github"]["branch"])
        else:
            repo.create_file(dosya_adi, msg, out.getvalue(), branch=st.secrets["github"]["branch"])
        return "OK"
    except Exception as e:
        return str(e)

# --- 5. RESMİ ENFLASYON (CACHED) ---
@st.cache_data(ttl=3600, show_spinner=False)
def get_official_inflation():
    api_key = st.secrets.get("evds", {}).get("api_key")
    if not api_key: return None, "API Key Yok"
    start_date = (datetime.now() - timedelta(days=365)).strftime("%d-%m-%Y")
    end_date = datetime.now().strftime("%d-%m-%Y")
    url = f"https://evds2.tcmb.gov.tr/service/evds/series=TP.FG.J0&startDate={start_date}&endDate={end_date}&type=json"
    headers = {'User-Agent': 'Mozilla/5.0', 'key': api_key, 'Accept': 'application/json'}
    try:
        url_with_key = f"{url}&key={api_key}"
        res = requests.get(url_with_key, headers=headers, timeout=10, verify=False)
        if res.status_code == 200:
            data = res.json()
            if "items" in data:
                df_evds = pd.DataFrame(data["items"])
                df_evds = df_evds[['Tarih', 'TP_FG_J0']]
                df_evds.columns = ['Tarih', 'Resmi_TUFE']
                df_evds['Tarih'] = pd.to_datetime(df_evds['Tarih'] + "-01", format="%Y-%m-%d")
                df_evds['Resmi_TUFE'] = pd.to_numeric(df_evds['Resmi_TUFE'], errors='coerce')
                return df_evds, "OK"
        return None, "Hata"
    except Exception as e:
        return None, str(e)

# --- 6. SCRAPER YARDIMCILARI ---
def temizle_fiyat(t):
    if not t: return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    t = t.replace('.', '').replace(',', '.') if ',' in t and '.' in t else t.replace(',', '.')
    try:
        return float(re.sub(r'[^\d.]', '', t))
    except:
        return None

def kod_standartlastir(k): return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, url):
    fiyat = 0; kaynak = ""; domain = url.lower() if url else ""
    # Basit Regex ve CSS arama (Detaylı scraper kısaltıldı, mantık aynı)
    if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
        if v := temizle_fiyat(m.group(1)): fiyat = v; kaynak = "Regex"
    return fiyat, kaynak

def html_isleyici(progress_callback):
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    progress_callback(0.05) 
    try:
        df_conf = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
        df_conf.columns = df_conf.columns.str.strip()
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), None)
        url_col = next((c for c in df_conf.columns if c.lower() == 'url'), None)
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde adı')
        if not kod_col or not url_col: return "Hata: Excel sütunları eksik."
        df_conf['Kod'] = df_conf[kod_col].astype(str).apply(kod_standartlastir)
        url_map = {str(row[url_col]).strip(): row for _, row in df_conf.iterrows() if pd.notna(row[url_col])}
        veriler = []
        islenen_kodlar = set()
        bugun = datetime.now().strftime("%Y-%m-%d")
        simdi = datetime.now().strftime("%H:%M")
        
        progress_callback(0.10)
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        total_zips = len(zip_files)
        
        for i, zip_file in enumerate(zip_files):
            current_progress = 0.10 + (0.80 * ((i + 1) / max(1, total_zips)))
            progress_callback(current_progress)
            try:
                blob = repo.get_git_blob(zip_file.sha)
                zip_data = base64.b64decode(blob.content)
                with zipfile.ZipFile(BytesIO(zip_data)) as z:
                    for file_name in z.namelist():
                        if not file_name.endswith(('.html', '.htm')): continue
                        with z.open(file_name) as f:
                            raw = f.read().decode("utf-8", errors="ignore")
                            soup = BeautifulSoup(raw, 'html.parser')
                            found_url = None
                            if c := soup.find("link", rel="canonical"): found_url = c.get("href")
                            if found_url and str(found_url).strip() in url_map:
                                target = url_map[str(found_url).strip()]
                                if target['Kod'] in islenen_kodlar: continue
                                fiyat, kaynak = fiyat_bul_siteye_gore(soup, target[url_col])
                                if fiyat > 0:
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'],
                                                    "Madde_Adi": target[ad_col], "Fiyat": float(fiyat),
                                                    "Kaynak": kaynak, "URL": target[url_col]})
                                    islenen_kodlar.add(target['Kod'])
            except: pass
        
        progress_callback(0.95)
        if veriler:
            return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else:
            return "Veri bulunamadı."
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 7. STATİK ANALİZ MOTORU ---
def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    df_clean = df_analiz.dropna(subset=['Fark'])
    toplam_urun = len(df_clean)
    artanlar = df_clean[df_clean['Fark'] > 0]
    dusenler = df_clean[df_clean['Fark'] < 0]
    sabitler = df_clean[df_clean['Fark'] == 0]
    artan_sayisi = len(artanlar)
    yayilim_orani = (artan_sayisi / toplam_urun) * 100 if toplam_urun > 0 else 0
    inc = df_clean.sort_values('Fark', ascending=False).head(5)
    dec = df_clean.sort_values('Fark', ascending=True).head(5)
    inc_str = "\n".join([f"   🔴 %{row['Fark']*100:5.2f} | {row[ad_col]}" for _, row in inc.iterrows()])
    dec_str = "\n".join([f"   🟢 %{abs(row['Fark']*100):5.2f} | {row[ad_col]}" for _, row in dec.iterrows()])

    text = f"""
**PİYASA GÖRÜNÜM RAPORU**
**Tarih:** {tarih}

**1. 📊 ANA GÖSTERGELER**
-----------------------------------------
**GENEL ENFLASYON** : **%{enf_genel:.2f}**
**GIDA ENFLASYONU** : **%{enf_gida:.2f}**
**AY SONU TAHMİNİ** : **%{tahmin:.2f}**
-----------------------------------------

**2. 🔎 PİYASA RÖNTGENİ**
**Fiyat Hareketleri:**
   🔺 **Zamlanan Ürün:** {artan_sayisi} adet
   🔻 **İndirimli Ürün:** {len(dusenler)} adet
   ➖ **Fiyatı Değişmeyen:** {len(sabitler)} adet

**Sepet Yayılımı:**
   Her 100 üründen **{int(yayilim_orani)}** tanesinde fiyat artışı tespit edilmiştir.

**3. ⚡ DİKKAT ÇEKEN ÜRÜNLER**

**▲ Yüksek Artışlar (Cep Yakanlar)**
{inc_str}

**▼ Fiyat Düşüşleri (Fırsatlar)**
{dec_str}

**4. 💡 SONUÇ**
Tahmin modelimiz, ay sonu kapanışının **%{tahmin:.2f}** bandında olacağını öngörmektedir.

---
*Otomatik Rapor Sistemi | Validasyon Müdürlüğü*
"""
    return text.strip()

# --- YENİ YARDIMCI FONKSİYONLAR ---
def make_neon_chart(fig):
    new_traces = []
    for trace in fig.data:
        if trace.type == 'scatter' or trace.type == 'line':
            glow_trace = go.Scatter(
                x=trace.x, y=trace.y, mode='lines',
                line=dict(width=10, color=trace.line.color), opacity=0.2, hoverinfo='skip', showlegend=False
            )
            new_traces.append(glow_trace)
    fig.add_traces(new_traces)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(showgrid=False, zeroline=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False))
    return fig

def style_chart(fig, is_pdf=False, is_sunburst=False):
    if is_pdf:
        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
    else:
        layout_args = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12), margin=dict(l=0, r=0, t=40, b=0))
        if not is_sunburst:
            layout_args.update(dict(xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="rgba(255,255,255,0.1)", gridcolor='rgba(255,255,255,0.05)', dtick="M1"),
                                    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False, gridwidth=1)))
        fig.update_layout(**layout_args)
    return fig

# --- 9. VERİ VE HESAPLAMA MOTORLARI (CACHE) ---

# 1. VERİ GETİR
@st.cache_data(ttl=600, show_spinner=False)
def verileri_getir_cache():
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    if df_f.empty or df_s.empty: return None, None, None

    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
    raw_dates = df_f['Tarih_Str'].unique().tolist()

    df_s.columns = df_s.columns.str.strip()
    kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
    ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
    df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
    df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
    df_s = df_s.drop_duplicates(subset=['Kod'], keep='first')
    df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
    df_f = df_f[df_f['Fiyat'] > 0]
    
    pivot = df_f.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat', aggfunc='mean')
    pivot = pivot.ffill(axis=1).bfill(axis=1).reset_index()
    if pivot.empty: return None, None, None

    if 'Grup' not in df_s.columns:
        grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut"}
        df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")

    df_analiz_base = pd.merge(df_s, pivot, on='Kod', how='left')
    return df_analiz_base, raw_dates, ad_col

# 2. HESAPLAMA YAP (CACHED)
@st.cache_data(show_spinner=False)
def hesapla_metrikler(df_analiz_base, secilen_tarih, gunler, tum_gunler_sirali, ad_col, agirlik_col, baz_col, aktif_agirlik_col, son):
    df_analiz = df_analiz_base.copy()
    for col in gunler: df_analiz[col] = pd.to_numeric(df_analiz[col], errors='coerce')
    dt_son = datetime.strptime(son, '%Y-%m-%d')
    if baz_col in df_analiz.columns: df_analiz[baz_col] = df_analiz[baz_col].fillna(df_analiz[son])
    df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz.get(aktif_agirlik_col, 0), errors='coerce').fillna(0)
    gecerli_veri = df_analiz[df_analiz[aktif_agirlik_col] > 0].copy()
    
    def geo_mean(row):
        vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
        return np.exp(np.mean(np.log(vals))) if vals else np.nan

    bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
    bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
    if not bu_ay_cols: bu_ay_cols = [son]
    
    gecerli_veri['Aylik_Ortalama'] = gecerli_veri[bu_ay_cols].apply(geo_mean, axis=1)
    gecerli_veri = gecerli_veri.dropna(subset=['Aylik_Ortalama', baz_col])

    enf_genel = 0.0; enf_gida = 0.0
    if not gecerli_veri.empty:
        w = gecerli_veri[aktif_agirlik_col]
        p_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
        if w.sum() > 0: enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
        
        gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
        if not gida_df.empty and gida_df[aktif_agirlik_col].sum() > 0:
            enf_gida = ((gida_df[aktif_agirlik_col] * (gida_df['Aylik_Ortalama']/gida_df[baz_col])).sum() / gida_df[aktif_agirlik_col].sum() * 100) - 100
            
        df_analiz['Fark'] = 0.0
        df_analiz.loc[gecerli_veri.index, 'Fark'] = (gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]) - 1
        df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100
    
    gun_farki = 0
    if len(gunler) >= 2:
        onceki_gun = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki_gun].replace(0, np.nan)) - 1
    else:
        df_analiz['Gunluk_Degisim'] = 0
        onceki_gun = son

    month_end_forecast = 0.0
    target_fixed = f"{dt_son.year}-{dt_son.month:02d}-31"
    fixed_cols = [c for c in tum_gunler_sirali if c.startswith(bu_ay_str) and c <= target_fixed]
    if fixed_cols and not gecerli_veri.empty:
        gecerli_veri['Fixed_Ort'] = gecerli_veri[fixed_cols].apply(geo_mean, axis=1)
        gecerli_t = gecerli_veri.dropna(subset=['Fixed_Ort'])
        if not gecerli_t.empty and gecerli_t[aktif_agirlik_col].sum() > 0:
             month_end_forecast = ((gecerli_t[aktif_agirlik_col] * (gecerli_t['Fixed_Ort']/gecerli_t[baz_col])).sum() / gecerli_t[aktif_agirlik_col].sum() * 100) - 100

    resmi_aylik_degisim = 0.0
    try:
        df_resmi, _ = get_official_inflation()
        if df_resmi is not None and not df_resmi.empty:
             df_resmi = df_resmi.sort_values('Tarih')
             if len(df_resmi) >= 2:
                 son_endeks = df_resmi.iloc[-1]['Resmi_TUFE']
                 onceki_endeks = df_resmi.iloc[-2]['Resmi_TUFE']
                 resmi_aylik_degisim = ((son_endeks / onceki_endeks) - 1) * 100
    except:
        resmi_aylik_degisim = 0.0

    return {
        "df_analiz": df_analiz, "enf_genel": enf_genel, "enf_gida": enf_gida,
        "tahmin": month_end_forecast, "resmi_aylik_degisim": resmi_aylik_degisim,
        "son": son, "onceki_gun": onceki_gun, "gunler": gunler,
        "ad_col": ad_col, "agirlik_col": aktif_agirlik_col, "baz_col": baz_col, "gun_farki": gun_farki,
        "stats_urun": len(df_analiz), "stats_kategori": df_analiz['Grup'].nunique(),
        "stats_veri_noktasi": len(df_analiz) * len(tum_gunler_sirali)
    }

# 3. SIDEBAR UI
def ui_sidebar_ve_veri_hazirlama(df_analiz_base, raw_dates, ad_col):
    if df_analiz_base is None: return None
    st.sidebar.markdown("### ⚙️ Veri Ayarları")
    BASLANGIC_LIMITI = "2026-02-04"
    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    if not tum_tarihler:
        st.sidebar.warning("Veri henüz oluşmadı.")
        return None
    secilen_tarih = st.sidebar.selectbox("Rapor Tarihi:", options=tum_tarihler, index=0)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 Piyasalar")
    symbols = [ {"s": "FX_IDC:USDTRY", "d": "Dolar / TL"}, {"s": "FX_IDC:EURTRY", "d": "Euro / TL"}, {"s": "FX_IDC:XAUTRYG", "d": "Gram Altın"} ]
    for sym in symbols:
        widget_code = f"""<div class="tradingview-widget-container" style="border-radius:12px; overflow:hidden; margin-bottom:10px;"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{{ "symbol": "{sym['s']}", "width": "100%", "height": 80, "locale": "tr", "dateRange": "1D", "colorTheme": "dark", "isTransparent": true, "autosize": true, "largeChartUrl": "" }}</script></div>"""
        with st.sidebar: components.html(widget_code, height=90)
    
    tum_gunler_sirali = sorted([c for c in df_analiz_base.columns if re.match(r'\d{4}-\d{2}-\d{2}', str(c)) and c >= BASLANGIC_LIMITI])
    if secilen_tarih in tum_gunler_sirali:
        idx = tum_gunler_sirali.index(secilen_tarih)
        gunler = tum_gunler_sirali[:idx+1]
    else: gunler = tum_gunler_sirali
    if not gunler: return None
    son = gunler[-1]; dt_son = datetime.strptime(son, '%Y-%m-%d')
    col_w25, col_w26 = 'Agirlik_2025', 'Agirlik_2026'
    ZINCIR_TARIHI = datetime(2026, 2, 4)
    if dt_son >= ZINCIR_TARIHI:
        aktif_agirlik_col = col_w26
        gunler_2026 = [c for c in tum_gunler_sirali if c >= "2026-01-01"]
        baz_col = gunler_2026[0] if gunler_2026 else gunler[0]
    else:
        aktif_agirlik_col = col_w25; baz_col = gunler[0]

    ctx = hesapla_metrikler(df_analiz_base, secilen_tarih, gunler, tum_gunler_sirali, ad_col, agirlik_col=None, baz_col=baz_col, aktif_agirlik_col=aktif_agirlik_col, son=son)
    return ctx

# --- SAYFA FONKSİYONLARI ---
def sayfa_ana_sayfa(ctx):
    urun_sayisi = ctx["stats_urun"] if ctx else "..."
    kategori_sayisi = ctx["stats_kategori"] if ctx else "..."
    veri_noktasi = ctx["stats_veri_noktasi"] if ctx else "..."
    st.markdown(f"""<div style="text-align:center; padding: 40px 20px;"><h1 style="font-size: 56px; font-weight: 800; margin-bottom: 20px; background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Gerçek Enflasyonu Keşfedin</h1><div style="display:flex; justify-content:center; gap:30px; flex-wrap:wrap;"><div class="kpi-card" style="width:250px; text-align:center; padding:30px;"><div style="font-size:42px; margin-bottom:10px;">📦</div><div style="font-size:32px; font-weight:bold; color:#fff;">{urun_sayisi}</div><div style="color:#a1a1aa; font-size:14px; font-weight:600;">TAKİP EDİLEN ÜRÜN</div></div><div class="kpi-card" style="width:250px; text-align:center; padding:30px;"><div style="font-size:42px; margin-bottom:10px;">📊</div><div style="font-size:32px; font-weight:bold; color:#fff;">{kategori_sayisi}</div><div style="color:#a1a1aa; font-size:14px; font-weight:600;">ANA KATEGORİ</div></div></div></div>""", unsafe_allow_html=True)

def sayfa_piyasa_ozeti(ctx):
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-title">GENEL ENFLASYON</div><div class="kpi-value">%{ctx["enf_genel"]:.2f}</div><div class="kpi-sub" style="color:#ef4444">Aylık Değişim</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-title">GIDA ENFLASYONU</div><div class="kpi-value">%{ctx["enf_gida"]:.2f}</div><div class="kpi-sub" style="color:#fca5a5">Mutfak Sepeti</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-title">AY SONU BEKLENTİ</div><div class="kpi-value">%{ctx["tahmin"]:.2f}</div><div class="kpi-sub" style="color:#a78bfa">AI Projeksiyonu</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-title">RESMİ (TÜİK) VERİSİ</div><div class="kpi-value">%{ctx["resmi_aylik_degisim"]:.2f}</div><div class="kpi-sub" style="color:#fbbf24">Son Açıklanan Aylık</div></div>', unsafe_allow_html=True)
    
    df = ctx["df_analiz"]
    inc = df.sort_values('Gunluk_Degisim', ascending=False).head(5)
    dec = df.sort_values('Gunluk_Degisim', ascending=True).head(5)
    items = []
    for _, r in inc.iterrows():
        if r['Gunluk_Degisim'] > 0: items.append(f"<span style='color:#f87171'>▲ {r[ctx['ad_col']]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    for _, r in dec.iterrows():
        if r['Gunluk_Degisim'] < 0: items.append(f"<span style='color:#34d399'>▼ {r[ctx['ad_col']]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    st.markdown(f"""<div class="ticker-wrap"><div class="ticker-move">{" &nbsp;&nbsp; • &nbsp;&nbsp; ".join(items)}</div></div>""", unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        fig_hist = px.histogram(df, x="Fark_Yuzde", nbins=20, title="Fiyat Değişim Dağılımı", color_discrete_sequence=["#3b82f6"])
        fig_hist.update_xaxes(visible=False)
        st.plotly_chart(style_chart(fig_hist), use_container_width=True)
    with col_g2:
        st.markdown(f"""<div class="smart-card"><div class="sc-title">YÜKSELENLER</div><div class="sc-val" style="color:#ef4444">{len(df[df['Fark'] > 0])} Ürün</div></div><div class="smart-card" style="margin-top:10px;"><div class="sc-title">DÜŞENLER</div><div class="sc-val" style="color:#10b981">{len(df[df['Fark'] < 0])} Ürün</div></div>""", unsafe_allow_html=True)

def sayfa_kategori_detay(ctx):
    df = ctx["df_analiz"]
    col_sel, col_src = st.columns([1, 2])
    kategoriler = ["Tümü"] + sorted(df['Grup'].unique().tolist())
    secilen_kat = col_sel.selectbox("Kategori Seç:", kategoriler)
    arama = col_src.text_input("Ürün Ara:", placeholder="Örn: Süt...")
    df_show = df.copy()
    if secilen_kat != "Tümü": df_show = df_show[df_show['Grup'] == secilen_kat]
    if arama: df_show = df_show[df_show[ctx['ad_col']].astype(str).str.contains(arama, case=False, na=False)]
    if not df_show.empty:
        items_per_page = 16
        page_num = st.number_input("Sayfa", min_value=1, max_value=max(1, len(df_show)//items_per_page + 1), step=1)
        batch = df_show.iloc[(page_num - 1) * items_per_page : (page_num - 1) * items_per_page + items_per_page]
        cols = st.columns(4)
        for idx, row in enumerate(batch.to_dict('records')):
            fiyat = row[ctx['son']]; fark = row.get('Gunluk_Degisim', 0) * 100
            cls = "pg-red" if fark > 0 else ("pg-green" if fark < 0 else "pg-yellow")
            icon = "▲" if fark > 0 else ("▼" if fark < 0 else "-")
            with cols[idx % 4]:
                st.markdown(f"""<div class="pg-card"><div class="pg-name">{row[ctx['ad_col']]}</div><div class="pg-price">{fiyat:.2f} ₺</div><div class="pg-badge {cls}">{icon} %{fark:.2f}</div></div><div style="margin-bottom:15px;"></div>""", unsafe_allow_html=True)
    else: st.info("Kriterlere uygun ürün bulunamadı.")

def sayfa_tam_liste(ctx):
    df = ctx["df_analiz"]
    def fix_sparkline(row):
        vals = row.tolist(); 
        if vals and min(vals) == max(vals): vals[-1] += 0.00001
        return vals
    df['Fiyat_Trendi'] = df[ctx['gunler']].apply(fix_sparkline, axis=1)
    cols_show = ['Grup', ctx['ad_col'], 'Fiyat_Trendi', ctx['baz_col'], 'Gunluk_Degisim']
    if ctx['baz_col'] != ctx['son']: cols_show.insert(3, ctx['son'])
    cfg = {"Fiyat_Trendi": st.column_config.LineChartColumn("Trend", width="small", y_min=0), ctx['ad_col']: "Ürün Adı", "Gunluk_Degisim": st.column_config.ProgressColumn("Değişim", format="%.2f%%", min_value=-0.5, max_value=0.5)}
    st.data_editor(df[cols_show], column_config=cfg, hide_index=True, use_container_width=True, height=600)
    output = BytesIO(); 
    with pd.ExcelWriter(output) as writer: df.to_excel(writer, index=False)
    st.download_button("📥 Excel Olarak İndir", data=output.getvalue(), file_name="Veri_Seti.xlsx")

def sayfa_raporlama(ctx):
    rap_text = generate_detailed_static_report(ctx["df_analiz"], ctx["son"], ctx["enf_genel"], ctx["enf_gida"], ctx["gun_farki"], ctx["tahmin"], ctx["ad_col"], ctx["agirlik_col"])
    st.markdown(f"""<div style="background:rgba(255,255,255,0.03); padding:30px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); font-family:'Inter'; line-height:1.8;">{rap_text.replace(chr(10), '<br>').replace('**', '<b>').replace('**', '</b>')}</div>""", unsafe_allow_html=True)
    word_buffer = create_word_report(rap_text, ctx["son"], ctx["df_analiz"])
    st.download_button(label="📥 Word Raporu İndir", data=word_buffer, file_name="Strateji_Raporu.docx", type="primary")

def sayfa_maddeler(ctx):
    df = ctx["df_analiz"]; kategoriler = sorted(df['Grup'].unique().tolist())
    secilen_kat = st.selectbox("Kategori Seçiniz:", options=kategoriler, index=0)
    df_sub = df[df['Grup'] == secilen_kat].copy().sort_values('Fark_Yuzde', ascending=True)
    if not df_sub.empty:
        colors = ['#10b981' if x < 0 else '#ef4444' for x in df_sub['Fark_Yuzde']]
        fig = go.Figure(go.Bar(x=df_sub['Fark_Yuzde'], y=df_sub[ctx['ad_col']], orientation='h', marker_color=colors, text=df_sub['Fark_Yuzde'].apply(lambda x: f"%{x:.2f}"), textposition='outside'))
        fig.update_layout(height=max(500, len(df_sub) * 30), title=f"{secilen_kat} Grubu Fiyat Değişimleri", margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else: st.warning("Bu kategoride veri bulunamadı.")

def sayfa_trend_analizi(ctx):
    df = ctx["df_analiz"]; gunler = ctx["gunler"]; agirlik_col = ctx["agirlik_col"]
    endeks_verisi = []
    for gun in gunler:
        temp_df = df.dropna(subset=[gun, agirlik_col])
        if not temp_df.empty and temp_df[agirlik_col].sum() > 0:
            index_val = (temp_df[gun] * temp_df[agirlik_col]).sum() / temp_df[agirlik_col].sum()
            endeks_verisi.append({"Tarih": gun, "Deger": index_val})
    df_endeks = pd.DataFrame(endeks_verisi)
    if not df_endeks.empty:
        df_endeks['Kümülatif_Degisim'] = ((df_endeks['Deger'] / df_endeks.iloc[0]['Deger']) - 1) * 100
        fig_genel = make_neon_chart(px.line(df_endeks, x='Tarih', y='Kümülatif_Degisim', title="GENEL ENFLASYON TRENDİ", markers=True))
        fig_genel.update_traces(line_color='#3b82f6', line_width=4)
        st.plotly_chart(style_chart(fig_genel), use_container_width=True)

    seçilen_urunler = st.multiselect("Grafiğe eklenecek ürünleri seçin:", options=df[ctx['ad_col']].unique(), default=df.sort_values('Fark_Yuzde', ascending=False).head(3)[ctx['ad_col']].tolist())
    if seçilen_urunler:
        df_melted = df[df[ctx['ad_col']].isin(seçilen_urunler)][[ctx['ad_col']] + gunler].melt(id_vars=[ctx['ad_col']], var_name='Tarih', value_name='Fiyat')
        base_prices = df_melted[df_melted['Tarih'] == gunler[0]].set_index(ctx['ad_col'])['Fiyat'].to_dict()
        df_melted['Yuzde_Degisim'] = df_melted.apply(lambda row: ((row['Fiyat']/base_prices.get(row[ctx['ad_col']], 1)) - 1)*100 if base_prices.get(row[ctx['ad_col']], 0) > 0 else 0, axis=1)
        st.plotly_chart(style_chart(px.line(df_melted, x='Tarih', y='Yuzde_Degisim', color=ctx['ad_col'], title="Ürün Bazlı Kümülatif Değişim (%)", markers=True)), use_container_width=True)

def sayfa_metodoloji(ctx=None):
    html_content = """
    <style>.method-card { background: rgba(26, 28, 35, 0.6); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 20px; margin-bottom: 20px; }</style>
    <h3>Metodoloji</h3>
    <div class="method-card"><b>1. Veri Toplama:</b> Web Scraping ile günlük fiyat takibi.</div>
    <div class="method-card"><b>2. Endeks:</b> Zincirleme Laspeyres formülü.</div>
    <div class="method-card"><b>3. Ağırlık:</b> TÜİK sepet ağırlıkları baz alınmıştır.</div>
    """
    st.markdown(html_content, unsafe_allow_html=True)

# --- ANA MAIN ---
def main():
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn2:
        if st.button("SİSTEMİ SENKRONİZE ET ⚡", type="primary", use_container_width=True):
            progress_bar = st.progress(0, text="Veri akışı sağlanıyor...")
            res = html_isleyici(lambda p: progress_bar.progress(min(1.0, max(0.0, p)), text="Senkronizasyon sürüyor..."))
            progress_bar.progress(1.0, text="Tamamlandı!"); time.sleep(0.5); progress_bar.empty()
            if "OK" in res:
                st.cache_data.clear(); st.toast('Sistem Senkronize Edildi!', icon='🚀'); time.sleep(1); st.rerun()
            else: st.error(res)

    with st.spinner("Veri tabanına bağlanılıyor..."):
        df_base, r_dates, col_name = verileri_getir_cache()
    
    if df_base is not None:
        ctx = ui_sidebar_ve_veri_hazirlama(df_base, r_dates, col_name)
    else:
        ctx = None

    menu_items = {
        "🏠 Ana Sayfa": "Ana Sayfa", "📊 Piyasa Özeti": "Piyasa Özeti", "📈 Trendler": "Trendler",
        "📦 Maddeler": "Maddeler", "🏷️ Kategori Detay": "Kategori Detay", "📋 Tam Liste": "Tam Liste",
        "📝 Raporlama": "Raporlama", "ℹ️ Metodoloji": "Metodoloji"
    }

    with st.sidebar:
        st.markdown("### 🧭 Menü")
        secilen_etiket = st.radio("Navigasyon", options=list(menu_items.keys()), label_visibility="collapsed", key="nav_radio")
    
    secim = menu_items[secilen_etiket]

    if ctx:
        if secim == "Ana Sayfa": sayfa_ana_sayfa(ctx)
        elif secim == "Piyasa Özeti": sayfa_piyasa_ozeti(ctx)
        elif secim == "Trendler": sayfa_trend_analizi(ctx)
        elif secim == "Maddeler": sayfa_maddeler(ctx)
        elif secim == "Kategori Detay": sayfa_kategori_detay(ctx)
        elif secim == "Tam Liste": sayfa_tam_liste(ctx)
        elif secim == "Raporlama": sayfa_raporlama(ctx)
        elif secim == "Metodoloji": sayfa_metodoloji(ctx)
    else:
        if secim == "Metodoloji": sayfa_metodoloji()
        else:
            err_msg = "<br><div style='text-align:center; padding:20px; background:rgba(255,0,0,0.1); border-radius:10px; color:#fff;'>⚠️ Veri seti yüklenemedi. Lütfen internet bağlantınızı kontrol edin.</div>"
            st.markdown(err_msg, unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px; opacity:0.6;">VALIDASYON MUDURLUGU © 2026 - GİZLİ ANALİZ BELGESİ</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
