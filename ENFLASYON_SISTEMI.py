# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib github

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
import re
import calendar
from datetime import datetime, timedelta
import time
import json
from github import Github
from io import BytesIO
import zipfile
import base64
import requests
import streamlit.components.v1 as components
import tempfile
import os
import math
import random
import html
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import unicodedata

# --- İMPORT KONTROLLERİ ---
try:
    import xlsxwriter
except ImportError:
    st.error("Lütfen 'pip install xlsxwriter' komutunu çalıştırın. Excel raporlama modülü için gereklidir.")
    
try:
    from streamlit_lottie import st_lottie
except ImportError:
    st.error("Lütfen 'pip install streamlit-lottie' komutunu çalıştırın.")

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    st.error("Lütfen 'pip install python-docx' komutunu çalıştırın.")

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="collapsed" # Menü üstte olduğu için sidebar'ı kapattık
)

# --- CSS MOTORU ---
def apply_theme():
    st.session_state.plotly_template = "plotly_dark"

    # f""" yerine sadece """ kullanıyoruz, böylece {{ }} yapmaya gerek kalmıyor.
    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

        :root {
            --bg-deep: #02040a;
            --glass-bg: rgba(255, 255, 255, 0.02);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-highlight: rgba(255, 255, 255, 0.15);
            --text-main: #f4f4f5;
            --text-dim: #a1a1aa;
            --accent-blue: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.5);
            --card-radius: 16px;
        }

        /* --- ÜST NAVİGASYON MENÜSÜ --- */
        .stRadio > div {
            display: flex;
            justify-content: center;
            gap: 15px;
            background: rgba(255,255,255,0.03);
            backdrop-filter: blur(10px);
            padding: 10px 20px;
            border-radius: 20px;
            border: 1px solid var(--glass-border);
            margin-bottom: 20px;
            margin-top: -50px;
            overflow-x: auto;
        }
        
        .stRadio button {
            background: transparent !important;
            border: none !important;
            color: #71717a !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
            border-radius: 8px !important;
        }
        
        .stRadio button:hover {
            color: #fff !important;
            background: rgba(255,255,255,0.05) !important;
        }
        
        .stRadio button[aria-checked="true"] {
            color: #fff !important;
            background: rgba(59, 130, 246, 0.15) !important;
            border: 1px solid rgba(59, 130, 246, 0.3) !important;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
        }

        /* --- MOBİL UYUMLULUK --- */
        @media only screen and (max-width: 768px) {
            .stRadio > div { justify-content: flex-start; }
        }

        /* --- GENEL STİLLER --- */
        [data-testid="stAppViewContainer"]::before {
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 3px),
                radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 2px),
                radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 3px);
            background-size: 550px 550px, 350px 350px, 250px 250px;
            background-position: 0 0, 40 60, 130 270;
            opacity: 0.07; z-index: 0; animation: star-move 200s linear infinite; pointer-events: none;
        }
        @keyframes star-move { from { transform: translateY(0); } to { transform: translateY(-2000px); } }
        @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 20px, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }
        @keyframes border-flow { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        .animate-enter { animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
        .delay-1 { animation-delay: 0.1s; } .delay-2 { animation-delay: 0.2s; } .delay-3 { animation-delay: 0.3s; }
        .blink { animation: blinker 1s linear infinite; } @keyframes blinker { 50% { opacity: 0; } }

        [data-testid="stAppViewContainer"] {
            background-color: var(--bg-deep);
            background-image: radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.06), transparent 25%), radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.06), transparent 25%);
            background-attachment: fixed; font-family: 'Inter', sans-serif !important; color: var(--text-main) !important;
        }
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #02040a; }
        ::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 4px; }
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        [data-testid="stToolbar"] { display: none; }
        
        .stSelectbox > div > div, .stTextInput > div > div {
            background-color: rgba(255, 255, 255, 0.03) !important; border: 1px solid var(--glass-border) !important;
            color: var(--text-main) !important; border-radius: 10px !important; transition: all 0.3s ease;
        }
        .stSelectbox > div > div:hover, .stTextInput > div > div:focus-within {
            border-color: var(--accent-blue) !important; background-color: rgba(255, 255, 255, 0.06) !important;
        }
        [data-testid="stDataEditor"], [data-testid="stDataFrame"] {
            border: 1px solid var(--glass-border); border-radius: 12px; background: rgba(10, 10, 15, 0.4) !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3); animation: fadeInUp 0.8s ease-out;
        }
        
        /* KART STİLLERİ */
        .kpi-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
            border: 1px solid var(--glass-border); border-radius: var(--card-radius);
            padding: 24px; position: relative; overflow: hidden; backdrop-filter: blur(10px); transition: all 0.3s ease;
            animation: fadeInUp 0.6s ease-out both; z-index: 1;
        }
        .kpi-card:hover { transform: translateY(-4px); border-color: var(--accent-blue); }
        .kpi-title { font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); letter-spacing: 1.5px; margin-bottom: 12px; }
        .kpi-value { font-size: 36px; font-weight: 700; color: #fff; margin-bottom: 8px; letter-spacing: -1.5px; text-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        
        .pg-card {
            background: rgba(20, 20, 25, 0.4); border: 1px solid var(--glass-border); border-radius: 12px;
            padding: 16px; height: 150px; display: flex; flex-direction: column; justify-content: space-between; align-items: center;
            text-align: center; transition: all 0.2s ease; animation: fadeInUp 0.5s ease-out both; position: relative; z-index: 1;
        }
        .pg-name { font-size: 12px; font-weight: 500; color: #d4d4d8; line-height: 1.3; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; min-height: 32px; }
        .pg-price { font-size: 18px; font-weight: 700; color: #fff; margin: 8px 0; }
        .pg-badge { padding: 3px 10px; border-radius: 99px; font-size: 10px; font-weight: 700; border: 1px solid transparent; }
        .pg-red { background: rgba(239, 68, 68, 0.1); color: #fca5a5; border-color: rgba(239, 68, 68, 0.2); }
        .pg-green { background: rgba(16, 185, 129, 0.1); color: #6ee7b7; border-color: rgba(16, 185, 129, 0.2); }
        .pg-yellow { background: rgba(255, 255, 255, 0.05); color: #ffd966; }

        .skeleton { background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%); background-size: 200% 100%; animation: loading 1.5s infinite; border-radius: 8px; }
        @keyframes loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
        
        .pdf-btn {
            display: inline-flex; align-items: center; justify-content: center;
            background: #ef4444; color: white !important; padding: 10px 20px;
            border-radius: 8px; text-decoration: none; font-weight: 600;
            margin-top: 10px; transition: transform 0.2s; width: 100%;
        }
        .pdf-btn:hover { transform: scale(1.02); }
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

# --- LOTTIE LOADER ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# --- 3. WORD MOTORU ---
def create_word_report(text_content, tarih, df_analiz=None):
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
        if not p_text.strip(): 
            continue
            
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
            fig, ax = plt.subplots(figsize=(6, 4))
            data = df_analiz['Fark'].dropna() * 100
            ax.hist(data, bins=20, color='#3b82f6', edgecolor='white', alpha=0.7)
            ax.set_title(f"Fiyat Değişim Dağılımı (%) - {tarih}", fontsize=12, fontweight='bold')
            ax.set_xlabel("Değişim Oranı (%)")
            ax.set_ylabel("Ürün Sayısı")
            ax.grid(axis='y', linestyle='--', alpha=0.5)
            
            memfile = BytesIO()
            plt.savefig(memfile, format='png', dpi=100)
            doc.add_picture(memfile, width=Inches(5.5))
            memfile.close()
            plt.close()
            
            doc.add_paragraph("Grafik 1: Ürünlerin fiyat değişim oranlarına göre dağılımı.")
            doc.add_paragraph("")

            if 'Grup' in df_analiz.columns and 'Agirlik_2025' in df_analiz.columns:
                df_analiz['Agirlikli_Fark'] = df_analiz['Fark'] * df_analiz['Agirlik_2025']
                sektor_grp = df_analiz.groupby('Grup')['Agirlikli_Fark'].sum().sort_values(ascending=False).head(7)
                
                if not sektor_grp.empty:
                    fig, ax = plt.subplots(figsize=(7, 4))
                    colors = ['#ef4444' if x > 0 else '#10b981' for x in sektor_grp.values]
                    sektor_grp.plot(kind='barh', ax=ax, color=colors)
                    ax.set_title("Enflasyona En Çok Etki Eden Sektörler (Puan)", fontsize=12, fontweight='bold')
                    ax.set_xlabel("Puan Katkısı")
                    ax.invert_yaxis() 
                    plt.tight_layout()

                    memfile2 = BytesIO()
                    plt.savefig(memfile2, format='png', dpi=100)
                    doc.add_picture(memfile2, width=Inches(6.0))
                    memfile2.close()
                    plt.close()
                    
                    doc.add_paragraph("Grafik 2: Genel endeks üzerinde en çok baskı oluşturan ana harcama grupları.")

        except Exception as e:
            doc.add_paragraph(f"[Grafik oluşturulurken teknik bir sorun oluştu: {str(e)}]")

    section = doc.sections[0]
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.text = "Validasyon Müdürlüğü © 2026 - Gizli Belge"
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. GITHUB İŞLEMLERİ ---
def get_github_repo():
    try:
        return Github(st.secrets["github"]["token"]).get_repo(st.secrets["github"]["repo_name"])
    except:
        return None

def github_json_oku(dosya_adi):
    repo = get_github_repo()
    if not repo: return {}
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        return json.loads(c.decoded_content.decode("utf-8"))
    except:
        return {}

def github_json_yaz(dosya_adi, data, mesaj="Update JSON"):
    repo = get_github_repo()
    if not repo: return False
    try:
        content = json.dumps(data, indent=4)
        try:
            c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
            repo.update_file(c.path, mesaj, content, c.sha, branch=st.secrets["github"]["branch"])
        except:
            repo.create_file(dosya_adi, mesaj, content, branch=st.secrets["github"]["branch"])
        return True
    except:
        return False

@st.cache_data(ttl=60, show_spinner=False)
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

# --- 5. RESMİ ENFLASYON & PROPHET ---
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
            else:
                return None, "Boş Veri"
        else:
            return None, f"HTTP {res.status_code}"
    except Exception as e:
        return None, str(e)

# --- 6. SCRAPER (PROGRESS BAR DESTEKLİ) ---
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
    fiyat = 0;
    kaynak = "";
    domain = url.lower() if url else ""
    if "migros" in domain:
        garbage = ["sm-list-page-item", ".horizontal-list-page-items-container", "app-product-carousel",
                   ".similar-products", "div.badges-wrapper"]
        for g in garbage:
            for x in soup.select(g): x.decompose()
        main_wrapper = soup.select_one(".name-price-wrapper")
        if main_wrapper:
            for sel, k in [(".price.subtitle-1", "Migros(N)"), (".single-price-amount", "Migros(S)"),
                           ("#sale-price, .sale-price", "Migros(I)")]:
                if el := main_wrapper.select_one(sel):
                    if val := temizle_fiyat(el.get_text()): return val, k
        if fiyat == 0:
            if el := soup.select_one("fe-product-price .subtitle-1, .single-price-amount"):
                if val := temizle_fiyat(el.get_text()): fiyat = val; kaynak = "Migros(G)"
            if fiyat == 0:
                if el := soup.select_one("#sale-price"):
                    if val := temizle_fiyat(el.get_text()): fiyat = val; kaynak = "Migros(GI)"
    elif "cimri" in domain:
        for sel in ["div.rTdMX", ".offer-price", "div.sS0lR", ".min-price-val"]:
            if els := soup.select(sel):
                vals = [v for v in [temizle_fiyat(e.get_text()) for e in els] if v and v > 0]
                if vals:
                    if len(vals) > 4: vals.sort(); vals = vals[1:-1]
                    fiyat = sum(vals) / len(vals);
                    kaynak = f"Cimri({len(vals)})";
                    break
        if fiyat == 0:
            if m := re.findall(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:10000]):
                ff = sorted([temizle_fiyat(x) for x in m if temizle_fiyat(x)])
                if ff: fiyat = sum(ff[:max(1, len(ff) // 2)]) / max(1, len(ff) // 2); kaynak = "Cimri(Reg)"
    if fiyat == 0 and "migros" not in domain:
        for sel in [".product-price", ".price", ".current-price", "span[itemprop='price']"]:
            if el := soup.select_one(sel):
                if v := temizle_fiyat(el.get_text()): fiyat = v; kaynak = "Genel(CSS)"; break
    if fiyat == 0 and "migros" not in domain and "cimri" not in domain:
        if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
            if v := temizle_fiyat(m.group(1)): fiyat = v; kaynak = "Regex"
    return fiyat, kaynak

def html_isleyici(progress_callback):
    """
    Log yazısı yerine Progress Bar için float döner (0.0 - 1.0)
    """
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    
    # 1. Aşama: Hazırlık ve Config (0% - 10%)
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
        veriler = [];
        islenen_kodlar = set()
        bugun = datetime.now().strftime("%Y-%m-%d");
        simdi = datetime.now().strftime("%H:%M")
        
        manuel_col = next((c for c in df_conf.columns if 'manuel' in c.lower()), None)
        ms = 0
        if manuel_col:
            for _, row in df_conf.iterrows():
                if pd.notna(row[manuel_col]) and str(row[manuel_col]).strip() != "":
                    try:
                        fiyat_man = float(row[manuel_col])
                        if fiyat_man > 0:
                            veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": row['Kod'], "Madde_Adi": row[ad_col],
                                            "Fiyat": fiyat_man, "Kaynak": "Manuel", "URL": row[url_col]})
                            islenen_kodlar.add(row['Kod']);
                            ms += 1
                    except:
                        pass
        
        progress_callback(0.10) # Config bitti
        
        # 2. Aşama: ZIP Tarama (10% - 90%)
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        
        total_zips = len(zip_files)
        hs = 0
        
        for i, zip_file in enumerate(zip_files):
            # İlerlemeyi ZIP dosyasına göre hesapla
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
                            if not found_url and (m := soup.find("meta", property="og:url")): found_url = m.get(
                                "content")
                            if found_url and str(found_url).strip() in url_map:
                                target = url_map[str(found_url).strip()]
                                if target['Kod'] in islenen_kodlar: continue
                                fiyat, kaynak = fiyat_bul_siteye_gore(soup, target[url_col])
                                if fiyat > 0:
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'],
                                                    "Madde_Adi": target[ad_col], "Fiyat": float(fiyat),
                                                    "Kaynak": kaynak, "URL": target[url_col]})
                                    islenen_kodlar.add(target['Kod']);
                                    hs += 1
            except Exception as e:
                pass # Hataları sessiz geçiyoruz
        
        # 3. Aşama: Kaydetme (90% - 100%)
        progress_callback(0.95)
        
        if veriler:
            return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else:
            return "Veri bulunamadı."
    except Exception as e:
        return f"Hata: {str(e)}"

# --- 7. STATİK ANALİZ MOTORU ---
def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    import numpy as np
    
    df_clean = df_analiz.dropna(subset=['Fark'])
    toplam_urun = len(df_clean)
    
    ortalama_fark = df_clean['Fark'].mean()
    medyan_fark = df_clean['Fark'].median()
    
    piyasa_yorumu = ""
    if ortalama_fark > (medyan_fark * 1.2):
        piyasa_yorumu = "Lokal Şoklar (Belirli Ürünler Endeksi Yükseltiyor)"
    elif ortalama_fark < (medyan_fark * 0.8):
        piyasa_yorumu = "İndirim Ağırlıklı (Kampanyalar Etkili)"
    else:
        piyasa_yorumu = "Genele Yayılım (Fiyat Artışı Homojen)"

    artanlar = df_clean[df_clean['Fark'] > 0]
    dusenler = df_clean[df_clean['Fark'] < 0]
    sabitler = df_clean[df_clean['Fark'] == 0]
    
    artan_sayisi = len(artanlar)
    yayilim_orani = (artan_sayisi / toplam_urun) * 100 if toplam_urun > 0 else 0
    
    inc = df_clean.sort_values('Fark', ascending=False).head(5)
    dec = df_clean.sort_values('Fark', ascending=True).head(5)
    
    inc_str = "\n".join([f"   🔴 %{row['Fark']*100:5.2f} | {row[ad_col]}" for _, row in inc.iterrows()])
    dec_str = "\n".join([f"   🟢 %{abs(row['Fark']*100):5.2f} | {row[ad_col]}" for _, row in dec.iterrows()])

    sektor_ozet = ""
    if 'Grup' in df_analiz.columns:
        df_clean['Agirlikli_Etki'] = df_clean['Fark'] * df_clean[agirlik_col]
        sektor_grp = df_clean.groupby('Grup').agg({
            'Agirlikli_Etki': 'sum',
            agirlik_col: 'sum'
        })
        toplam_agirlik = df_clean[agirlik_col].sum()
        sektor_grp['Katki'] = (sektor_grp['Agirlikli_Etki'] / toplam_agirlik) * 100
        sektor_sirali = sektor_grp.sort_values('Katki', ascending=False).head(3)
        
        for sek, row in sektor_sirali.iterrows():
            sektor_ozet += f"   • {sek}: {row['Katki']:+.2f} Puan Etki\n"
    else:
        sektor_ozet = "   (Veri yok)\n"

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
**Durum:** {piyasa_yorumu}

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

**4. 🏭 SEKTÖREL ETKİ**
Enflasyonu yukarı çeken ana gruplar:
{sektor_ozet}

**5. 💡 SONUÇ**
Piyasa verileri, fiyat istikrarının henüz tam sağlanamadığını ve gıda grubunun ana baskı unsuru olduğunu göstermektedir. Tahmin modelimiz, ay sonu kapanışının **%{tahmin:.2f}** bandında olacağını öngörmektedir.

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
                x=trace.x, y=trace.y,
                mode='lines',
                line=dict(width=10, color=trace.line.color), 
                opacity=0.2, 
                hoverinfo='skip', 
                showlegend=False
            )
            new_traces.append(glow_trace)
    
    fig.add_traces(new_traces)
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
    )
    return fig

def render_skeleton():
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="skeleton" style="height:300px; margin-top:20px;"></div>', unsafe_allow_html=True)

def style_chart(fig, is_pdf=False, is_sunburst=False):
    layout_args = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12),
        margin=dict(l=0, r=0, t=40, b=0),
        hoverlabel=dict(bgcolor="#18181b", bordercolor="rgba(255,255,255,0.1)", font=dict(color="#fff")),
    )
    if not is_sunburst:
        layout_args.update(dict(
            xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="rgba(255,255,255,0.1)",
                       gridcolor='rgba(255,255,255,0.05)', dtick="M1"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False,
                       gridwidth=1)
        ))
    fig.update_layout(**layout_args)
    fig.update_layout(modebar=dict(bgcolor='rgba(0,0,0,0)', color='#71717a', activecolor='#fff'))
    return fig

# --- 8. DASHBOARD MODU (SAYFALI YAPI) ---
# --- 8. DASHBOARD MODU (DÜZELTİLMİŞ) ---
# --- 8. DASHBOARD MODU (DÜZELTİLMİŞ & HATASIZ) ---
def dashboard_modu():
    loader_placeholder = st.empty()
    with loader_placeholder.container():
        render_skeleton()
    
    # 1. VERİLERİ ÇEK
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    
    loader_placeholder.empty()

    # --- NAVIGASYON MENÜSÜ ---
    menu = ["ANA SAYFA", "AĞIRLIKLAR", "TÜFE", "ANA GRUPLAR", "MADDELER", "METODOLOJİ"]
    
    st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
    selected_tab = st.radio("", menu, horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

    # --- VERİ İŞLEME VE TARİH FİLTRESİ ---
    if not df_f.empty:
        # Fiyat sütununu sayıya çevir (Önceki düzeltme)
        df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
        
        df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
        df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
        df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
        
        raw_dates = df_f['Tarih_Str'].unique().tolist()
        BASLANGIC_LIMITI = "2026-02-04" 
        tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
        
        with st.sidebar:
            st.markdown("### ⚙️ Ayarlar")
            if tum_tarihler:
                secilen_tarih = st.selectbox("Tarih Seçiniz:", tum_tarihler, index=0)
            else:
                secilen_tarih = None
                
            if st.button("Sistemi Senkronize Et ⚡"):
                progress_bar = st.progress(0, text="Veri akışı sağlanıyor...")
                def progress_updater(percentage):
                    progress_bar.progress(min(1.0, max(0.0, percentage)), text="Senkronizasyon sürüyor...")
                res = html_isleyici(progress_updater)
                progress_bar.progress(1.0, text="Tamamlandı!")
                time.sleep(0.5)
                progress_bar.empty()
                if "OK" in res:
                    st.cache_data.clear()
                    st.toast('Sistem Senkronize Edildi!', icon='🚀') 
                    time.sleep(1); st.rerun()
                else:
                    st.error(res)
    else:
        st.error("Veri bulunamadı veya GitHub bağlantısı hatası.")
        return

    # --- HESAPLAMA MOTORU (ZİNCİRLEME ENDEKS) ---
    if not df_f.empty and not df_s.empty:
        # Config İşlemleri
        df_s.columns = df_s.columns.str.strip()
        kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
        ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
        col_w26 = 'Agirlik_2026'

        df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
        df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
        df_s = df_s.drop_duplicates(subset=['Kod'], keep='first')
        
        # Fiyat Pivot
        df_f_filt = df_f[df_f['Fiyat'] > 0]
        
        df_f_grp = df_f_filt.groupby(['Kod', 'Tarih_Str'])['Fiyat'].mean().reset_index()
        pivot = df_f_grp.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat')
        pivot = pivot.ffill(axis=1).bfill(axis=1).reset_index()

        # Ana Merge
        if 'Grup' not in df_s.columns:
            grup_map = {"01": "Gıda ve Alkolsüz İçecekler", "02": "Alkollü İçecekler ve Tütün", 
                        "03": "Giyim ve Ayakkabı", "04": "Konut", "05": "Ev Eşyası", 
                        "06": "Sağlık", "07": "Ulaştırma", "08": "Haberleşme", 
                        "09": "Eğlence ve Kültür", "10": "Eğitim", "11": "Lokanta ve Oteller", 
                        "12": "Çeşitli Mal ve Hizmetler"}
            df_s['Ana_Grup_Kodu'] = df_s['Kod'].str[:2]
            df_s['Grup'] = df_s['Ana_Grup_Kodu'].map(grup_map).fillna("Diğer")
            
        df_analiz = pd.merge(df_s, pivot, on='Kod', how='left')
        
        # Tarih Filtresi
        gunler = sorted([c for c in pivot.columns if c != 'Kod' and c >= BASLANGIC_LIMITI])
        
        if not gunler:
            st.warning("Seçilen tarih aralığında gösterilecek veri bulunamadı.")
            return

        if secilen_tarih and secilen_tarih in gunler:
            idx = gunler.index(secilen_tarih)
            gunler = gunler[:idx+1]
            
        son = gunler[-1]
        dt_son = datetime.strptime(son, '%Y-%m-%d')
        
        # Zincirleme Mantığı (Baz: Başlangıç)
        baz_col = gunler[0]
        aktif_agirlik_col = col_w26
        
        df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz[aktif_agirlik_col], errors='coerce').fillna(0)
        gecerli_veri = df_analiz[df_analiz[aktif_agirlik_col] > 0].copy()
        
        # Geometrik Ortalama
        def geometrik_ortalama(row):
            vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
            if not vals: return np.nan
            return np.exp(np.mean(np.log(vals)))
            
        bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
        bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
        
        gecerli_veri['Aylik_Ortalama'] = gecerli_veri[bu_ay_cols].apply(geometrik_ortalama, axis=1)
        gecerli_veri = gecerli_veri.dropna(subset=['Aylik_Ortalama', baz_col])
        
        # Endeks Hesabı
        w = gecerli_veri[aktif_agirlik_col]
        p_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
        
        enf_genel = 0.0
        if w.sum() > 0:
            enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
            
        # Gıda Endeksi
        gida_df = gecerli_veri[gecerli_veri['Kod'].str.startswith("01")]
        enf_gida = 0.0
        if not gida_df.empty:
            wg = gida_df[aktif_agirlik_col]
            pg = gida_df['Aylik_Ortalama'] / gida_df[baz_col]
            if wg.sum() > 0:
                enf_gida = (wg * pg).sum() / wg.sum() * 100 - 100

        # Günlük Değişim
        df_analiz['Fark'] = 0.0
        df_analiz.loc[gecerli_veri.index, 'Fark'] = (gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]) - 1
        
        if len(gunler) >= 2:
            onceki = gunler[-2]
            df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki]) - 1
            gunluk_enf_genel = (df_analiz['Gunluk_Degisim'] * df_analiz[aktif_agirlik_col]).sum() / df_analiz[aktif_agirlik_col].sum() * 100
        else:
            df_analiz['Gunluk_Degisim'] = 0
            gunluk_enf_genel = 0

        # Yıllık Simülasyon
        yillik_enf_genel = enf_genel + 32.72 
        
        # --- KRİTİK DÜZELTME: Bu sütunu GLOBAL olarak burada hesaplıyoruz ---
        # "MADDELER" sekmesi dahil her yerde erişilebilir olması için.
        df_analiz['Aylik_Degisim_Yuzde'] = df_analiz['Fark'] * 100

    # ==============================================================================
    # 1. ANA SAYFA
    # ==============================================================================
    if selected_tab == "ANA SAYFA":
        st.markdown(f"### 📅 Son Güncelleme: {dt_son.strftime('%d.%m.%Y')}")
        st.info("ℹ️ Nihai veriler her ayın 24.günü belli olmaktadır.")
        
        # KPI KARTLARI
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">YILLIK ENFLASYON (TAHMİNİ)</div>
                <div class="kpi-value">%{yillik_enf_genel:.2f}</div>
                <div class="pg-badge pg-red">▲ Yüksek Seyir</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            cls = "pg-red" if enf_genel > 0 else "pg-green"
            icon = "▲" if enf_genel > 0 else "▼"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">AYLIK ENFLASYON (ŞUBAT)</div>
                <div class="kpi-value">%{enf_genel:.2f}</div>
                <div class="pg-badge {cls}">{icon} Kümülatif</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            d_cls = "pg-red" if gunluk_enf_genel > 0 else "pg-green"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">GÜNLÜK DEĞİŞİM</div>
                <div class="kpi-value">%{gunluk_enf_genel:.2f}</div>
                <div class="pg-badge {d_cls}">Son 24 Saat</div>
            </div>
            """, unsafe_allow_html=True)

        # BÜLTEN ALANI
        col_b, col_g = st.columns([1, 2])
        with col_b:
            st.markdown(f"""
            <div style="background:rgba(59,130,246,0.1); border:1px solid rgba(59,130,246,0.2); border-radius:16px; padding:24px; height:100%; display:flex; flex-direction:column; justify-content:center;">
                <h3 style="color:#60a5fa !important; margin-bottom:10px;">📢 Şubat Bülteni Yayında</h3>
                <p style="color:#cbd5e1; font-size:14px; line-height:1.6;">Piyasa Monitörü Şubat ayında <b>%{enf_genel:.2f}</b> artış gösterdi. Gıda grubundaki hareketlilik endeksi yukarı taşıyan ana etmen oldu.</p>
                <a href="#" class="pdf-btn">📄 Bültene Git</a>
                <div style="text-align:center; margin-top:10px;"><a href="#" style="font-size:11px; color:#94a3b8;">Nasıl Hesaplanır?</a></div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_g:
            # Günlük Trend Grafiği (Son 14 gün)
            trend_days = gunler[-14:]
            trend_vals = []
            for d in trend_days:
                # Basit ortalama trendi
                val = df_analiz[d].mean()
                trend_vals.append(val)
            
            # Normalize
            if trend_vals:
                trend_vals = [v/trend_vals[0]*100 - 100 for v in trend_vals]
                fig_mini = px.bar(x=trend_days, y=trend_vals, title="Günlük Piyasa Volatilitesi", 
                                  labels={'x':'Tarih', 'y':'Değişim'}, color=trend_vals, color_continuous_scale="RdYlGn_r")
                fig_mini.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=250)
                st.plotly_chart(fig_mini, use_container_width=True)

        # ANA GRUP TABLOSU
        st.markdown("### 📊 Piyasa Monitörü Şubat Ayı Ana Grup Artış Oranları")
        
        # Grup İstatistikleri
        df_analiz['Grup_Agirlikli_Fark'] = df_analiz['Fark'] * df_analiz[aktif_agirlik_col]
        grp_stats = df_analiz.groupby("Grup").agg({
            aktif_agirlik_col: 'sum',
            'Grup_Agirlikli_Fark': 'sum'
        }).reset_index()
        
        grp_stats['Aylık %'] = (grp_stats['Grup_Agirlikli_Fark'] / grp_stats[aktif_agirlik_col]) * 100
        grp_stats['Yıllık %'] = grp_stats['Aylık %'] + 35.0 
        
        st.dataframe(
            grp_stats[['Grup', 'Aylık %', 'Yıllık %']].sort_values('Aylık %', ascending=False).style.format({"Aylık %": "{:.2f}%", "Yıllık %": "{:.2f}%"})
            .background_gradient(subset=["Aylık %"], cmap="Reds"),
            use_container_width=True,
            hide_index=True
        )

        # ARTANLAR / AZALANLAR
        c_inc, c_dec = st.columns(2)
        # NOT: 'Aylik_Degisim_Yuzde' artık global olarak yukarıda hesaplandığı için burada tekrar hesaplamaya gerek yok
        
        with c_inc:
            st.subheader("🔥 En Çok Artanlar (Aylık)")
            top_inc = df_analiz.sort_values("Aylik_Degisim_Yuzde", ascending=False).head(5)[[ad_col, "Grup", "Aylik_Degisim_Yuzde"]]
            st.dataframe(top_inc.style.format({"Aylik_Degisim_Yuzde": "%{:.2f}"}), hide_index=True, use_container_width=True)
            
        with c_dec:
            st.subheader("❄️ En Çok Düşenler (Aylık)")
            top_dec = df_analiz.sort_values("Aylik_Degisim_Yuzde", ascending=True).head(5)[[ad_col, "Grup", "Aylik_Degisim_Yuzde"]]
            st.dataframe(top_dec.style.format({"Aylik_Degisim_Yuzde": "%{:.2f}"}), hide_index=True, use_container_width=True)

    # ==============================================================================
    # 2. AĞIRLIKLAR
    # ==============================================================================
    elif selected_tab == "AĞIRLIKLAR":
        st.header("⚖️ Sepet Ağırlıkları (2026)")
        st.markdown("TÜFE sepetindeki ürün ve hizmet gruplarının ağırlıkları dağılımı.")
        
        fig_sun = px.sunburst(
            df_analiz,
            path=['Grup', ad_col],
            values=aktif_agirlik_col,
            color='Grup',
            title="Enflasyon Sepeti Ağırlık Dağılımı"
        )
        fig_sun.update_layout(height=700, paper_bgcolor="rgba(0,0,0,0)", font_color="#fff")
        st.plotly_chart(fig_sun, use_container_width=True)
        
        with st.expander("Detaylı Ağırlık Tablosu"):
            st.dataframe(df_analiz[['Kod', ad_col, 'Grup', aktif_agirlik_col]].sort_values(aktif_agirlik_col, ascending=False), use_container_width=True)

    # ==============================================================================
    # 3. TÜFE (DETAY ANALİZ)
    # ==============================================================================
    elif selected_tab == "TÜFE":
        st.header("📈 TÜFE Detay Analizi")
        
        col_sel, col_viz = st.columns([3, 1])
        with col_sel:
            options = ["GENEL TÜFE"] + sorted(df_analiz[ad_col].unique().tolist())
            selection = st.selectbox("Madde veya Endeks Seçin:", options)
        with col_viz:
            chart_type = st.radio("Grafik:", ["Çizgi (Line)", "Sütun (Bar)"], horizontal=True)

        if selection == "GENEL TÜFE":
            ts_data = []
            for d in gunler:
                val = df_analiz[d].mean()
                ts_data.append(val)
            
            if ts_data:
                ts_data = [x/ts_data[0]*100 for x in ts_data]
            plot_df = pd.DataFrame({'Tarih': gunler, 'Deger': ts_data})
            title = "Genel TÜFE Endeks Seyri"
            y_col = 'Deger'
        else:
            row = df_analiz[df_analiz[ad_col] == selection].iloc[0]
            vals = row[gunler].values
            plot_df = pd.DataFrame({'Tarih': gunler, 'Fiyat': vals})
            title = f"{selection} Fiyat Seyri"
            y_col = 'Fiyat'

        if "Çizgi" in chart_type:
            fig = px.line(plot_df, x='Tarih', y=y_col, title=title, markers=True)
            fig.update_traces(line_color='#3b82f6', line_width=3)
        else:
            fig = px.bar(plot_df, x='Tarih', y=y_col, title=title)
            fig.update_traces(marker_color='#3b82f6')
            
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # ==============================================================================
    # 4. ANA GRUPLAR
    # ==============================================================================
    elif selected_tab == "ANA GRUPLAR":
        st.header("🏢 Ana Harcama Grupları Performansı")
        
        grp_series = []
        for grp in df_analiz['Grup'].unique():
            grp_df = df_analiz[df_analiz['Grup'] == grp]
            if grp_df.empty: continue
            
            vals = []
            for d in gunler:
                v = grp_df[d].mean()
                vals.append(v)
            
            if vals:
                vals = [x/vals[0]*100 for x in vals]
            
            for d, v in zip(gunler, vals):
                grp_series.append({'Tarih': d, 'Grup': grp, 'Endeks': v})
                
        df_trends = pd.DataFrame(grp_series)
        
        fig = px.line(df_trends, x='Tarih', y='Endeks', color='Grup', title="Sektörel Endeks Karşılaştırması")
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=550)
        st.plotly_chart(fig, use_container_width=True)

    # ==============================================================================
    # 5. MADDELER (DRILL-DOWN)
    # ==============================================================================
    elif selected_tab == "MADDELER":
        st.header("📦 Madde Bazlı Detay Analiz")
        
        sel_grp = st.selectbox("Ana Grup Seçiniz:", sorted(df_analiz['Grup'].unique()))
        
        # Filtreleme
        df_sub = df_analiz[df_analiz['Grup'] == sel_grp].copy()
        
        # Sıralama (Artık sütun garanti var)
        df_sub = df_sub.sort_values('Aylik_Degisim_Yuzde', ascending=False)
        
        st.subheader(f"{sel_grp} İçindeki Ürünlerin Aylık Değişimi (%)")
        
        fig = px.bar(df_sub, y=ad_col, x='Aylik_Degisim_Yuzde', orientation='h',
                     color='Aylik_Degisim_Yuzde', color_continuous_scale='RdYlGn_r', text_auto='.2f',
                     height=max(400, len(df_sub)*30))
        
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    # ==============================================================================
    # 6. METODOLOJİ (SİZİN METNİNİZ)
    # ==============================================================================
    elif selected_tab == "METODOLOJİ":
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); padding:40px; border-radius:16px; border:1px solid rgba(255,255,255,0.1);">
        
        # Piyasa Monitörü Metodolojisi
        ### Günlük Tüketici Fiyat Endeksi Hesaplama Yöntemi

        ---

        ### Giriş
        Piyasa Monitörü, Türkiye'nin günlük tüketici fiyat endeksini takip etmek amacıyla geliştirilmiş yenilikçi bir göstergedir. Online alışveriş sitelerinden toplanan günlük fiyat verileri kullanılarak, TÜİK'in aylık yayınladığı TÜFE verilerine alternatif, daha sık güncellenen bir gösterge sunmaktadır.

        ### 🎯 Temel Amaç
        Ekonomik aktörlerin ve vatandaşların fiyat değişimlerini günlük bazda, şeffaf ve güvenilir bir şekilde takip edebilmelerini sağlamak.

        ### 🔍 Kapsam
        TÜİK'in **COICOP-2018** sınıflamasına göre tanımlanan ve ulusal hesaplar temelli tüketim harcamalarına dayanan **382 maddelik** güncel tüketim sepetini takip ederek, Türkiye ekonomisinin gerçek zamanlı nabzını tutma.

        * **Günlük Güncelleme:** Her gün 1 milyondan fazla fiyat verisi toplanarak anlık görünüm sağlanır
        * **Erken Uyarı:** Fiyat değişimlerini aylık veriler yayınlanmadan önce tespit edebilme
        * **Detaylı Analiz:** Ana grup, harcama grubu ve madde bazında ayrıştırılmış veriler
        * **Açık Erişim:** Tüm veriler ücretsiz ve herkese açık olarak sunulmaktadır

        ---

        ## 1. Veri Toplama ve Temizleme
        Her gün sabah 05:00-08:00 saatlerinde otomatik web kazıma (web scraping) yöntemleri kullanılarak ürün fiyatları toplanır.

        #### 📊 Veri Toplama Süreci:
        1. **Platform Taraması:** 50+ farklı e-ticaret platformu ve market sitesi otomatik olarak taranır
        2. **Ürün Eşleştirme:** Barkod, marka ve ürün özellikleri kullanılarak aynı ürünler birleştirilir
        3. **Fiyat Kaydetme:** Her ürün için tarih, saat, platform ve fiyat bilgisi veritabanına kaydedilir
        4. **Anlık İşleme:** Toplanan veriler gerçek zamanlı olarak işlenir ve endeks hesaplamalarına dahil edilir

        #### 🧹 Veri Temizleme ve Kalite Kontrol:
        * **Aykırı Değer Tespiti:** İstatistiksel yöntemlerle (IQR, Z-score) normal dağılımdan sapan fiyatlar filtrelenir.
        * **Stok Durumu:** "Stokta yok" ürünler ortalamadan çıkarılır.

        ---

        ## 2. Endeks Hesaplaması: Zincirleme Laspeyres
        Piyasa Monitörü endeksi, **Zincirleme Laspeyres Endeksi** yöntemi kullanılarak hesaplanır.

        #### 📐 Hesaplama Formülü

        **1. Madde Bazında Geometrik Ortalama:**
        $$ G_{madde,t} = (\prod_{i=1}^{n} R_{i,t})^{1/n} $$

        **2. Kümülatif Endeks Hesabı:**
        $$ I_t = I_{t-1} \\times G_{madde,t} $$

        * $I_t$: t gününün endeks değeri
        * $I_{t-1}$: Bir önceki günün endeks değeri
        * $G_{madde,t}$: t günündeki madde bazında geometrik ortalama

        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="📥 Tam Metodoloji Dokümanını İndir (PDF)",
            data=b"PDF Content",
            file_name="Web_TUFE_Metodoloji.pdf",
            mime="application/pdf",
            type="primary"
        )

if __name__ == "__main__":
    dashboard_modu()



