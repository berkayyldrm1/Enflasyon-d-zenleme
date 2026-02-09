# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib

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
    st.error("Lütfen 'pip install xlsxwriter' komutunu çalıştırın.")
    
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
    initial_sidebar_state="expanded"
)

# --- CSS MOTORU ---
def apply_theme():
    st.session_state.plotly_template = "plotly_dark"

    final_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

        :root {{
            --bg-deep: #02040a;
            --glass-bg: rgba(255, 255, 255, 0.02);
            --glass-border: rgba(255, 255, 255, 0.08);
            --glass-highlight: rgba(255, 255, 255, 0.15);
            --text-main: #f4f4f5;
            --text-dim: #a1a1aa;
            --accent-blue: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.5);
            --card-radius: 16px;
        }}

        /* --- SAYFA ÜST BOŞLUĞUNU KALDIRMA --- */
        .block-container {{
            padding-top: 1rem !important; 
            padding-bottom: 1rem !important;
        }}
        
        /* Header Gizleme */
        header {{visibility: hidden;}}
        [data-testid="stHeader"] {{ visibility: hidden; height: 0px; }}
        [data-testid="stToolbar"] {{ display: none; }}

        /* --- MOBİL UYUMLULUK --- */
        @media only screen and (max-width: 768px) {{
            section[data-testid="stSidebar"] {{
                display: none !important;
                width: 0px !important;
            }}
            div[data-testid="stSidebarCollapsedControl"] {{
                display: none !important;
            }}
            .block-container {{
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
                max-width: 100% !important;
            }}
            .monitor-header {{
                flex-direction: column !important;
                gap: 10px !important;
                text-align: center !important;
                padding: 15px !important;
                height: auto !important;
            }}
            .mh-right {{ text-align: center !important; }}
            .kpi-card {{ margin-bottom: 10px !important; padding: 16px !important; }}
            .kpi-value {{ font-size: 24px !important; }}
            
            .stTabs [data-baseweb="tab-list"] {{
                overflow-x: auto !important;
                justify-content: flex-start !important;
            }}
        }}

        /* --- GENEL STİLLER --- */
        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                radial-gradient(white, rgba(255,255,255,.2) 2px, transparent 3px),
                radial-gradient(white, rgba(255,255,255,.15) 1px, transparent 2px),
                radial-gradient(white, rgba(255,255,255,.1) 2px, transparent 3px);
            background-size: 550px 550px, 350px 350px, 250px 250px;
            background-position: 0 0, 40 60, 130 270;
            opacity: 0.07; z-index: 0; animation: star-move 200s linear infinite; pointer-events: none;
        }}
        @keyframes star-move {{ from {{ transform: translateY(0); }} to {{ transform: translateY(-2000px); }} }}
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translate3d(0, 20px, 0); }} to {{ opacity: 1; transform: translate3d(0, 0, 0); }} }}
        @keyframes border-flow {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        .animate-enter {{ animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both; }}
        
        [data-testid="stAppViewContainer"] {{
            background-color: var(--bg-deep);
            background-image: radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.06), transparent 25%), radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.06), transparent 25%);
            background-attachment: fixed; font-family: 'Inter', sans-serif !important; color: var(--text-main) !important;
        }}
        
        section[data-testid="stSidebar"] {{
            background: linear-gradient(180deg, rgba(5, 5, 10, 0.95) 0%, rgba(0, 0, 0, 0.98) 100%) !important;
            border-right: 1px solid var(--glass-border); backdrop-filter: blur(20px); z-index: 99;
        }}
        
        .stSelectbox > div > div, .stTextInput > div > div {{
            background-color: rgba(255, 255, 255, 0.03) !important; border: 1px solid var(--glass-border) !important;
            color: var(--text-main) !important; border-radius: 10px !important;
        }}
        
        [data-testid="stDataEditor"], [data-testid="stDataFrame"] {{
            border: 1px solid var(--glass-border); border-radius: 12px; background: rgba(10, 10, 15, 0.4) !important;
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px; background: rgba(255,255,255,0.02); padding: 6px; border-radius: 12px; border: 1px solid var(--glass-border); margin-top: 10px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 36px; border-radius: 8px; padding: 0 15px; color: var(--text-dim) !important; font-weight: 500; border: none !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: rgba(255,255,255,0.1) !important; color: #fff !important;
        }}

        .kpi-card {{
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
            border: 1px solid var(--glass-border); border-radius: var(--card-radius);
            padding: 20px; position: relative; overflow: hidden; backdrop-filter: blur(10px);
            animation: fadeInUp 0.6s ease-out both; z-index: 1;
        }}
        .kpi-title {{ font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); letter-spacing: 1px; margin-bottom: 8px; }}
        .kpi-value {{ font-size: 32px; font-weight: 700; color: #fff; margin-bottom: 5px; letter-spacing: -1px; }}
        .kpi-sub {{ font-size: 11px; font-weight: 500; display: flex; align-items: center; gap: 6px; color: var(--text-dim); background: rgba(0,0,0,0.2); padding: 3px 6px; border-radius: 4px; width: fit-content; }}

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

        .ticker-wrap {{ width: 100%; overflow: hidden; background: rgba(0,0,0,0.2); border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border); padding: 8px 0; margin-bottom: 20px; white-space: nowrap; }}
        .ticker-move {{ display: inline-block; padding-left: 100%; animation: marquee 45s linear infinite; font-family: 'JetBrains Mono', monospace; font-size: 11px; }}
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}

        .smart-card {{ background: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 4px; }}
        .sc-title {{ font-size: 10px; color: #a1a1aa; font-weight:600; text-transform:uppercase; }}
        .sc-val {{ font-size: 18px; color: #fff; font-weight:700; }}
        
        .skeleton {{ background: rgba(255,255,255,0.05); animation: blinker 1.5s infinite; border-radius: 8px; }}
        
        /* BUTON STİLİ */
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
                # Veri temizliği ve kontrol
                if 'Fark' in df_analiz.columns:
                    data = pd.to_numeric(df_analiz['Fark'], errors='coerce').dropna() * 100
                    if not data.empty:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        ax.hist(data, bins=20, color='#3b82f6', edgecolor='white', alpha=0.7)
                        ax.set_title(f"Fiyat Değişim Dağılımı (%) - {tarih}", fontsize=12, fontweight='bold')
                        ax.set_xlabel("Değişim Oranı (%)")
                        ax.set_ylabel("Ürün Sayısı")
                        ax.grid(axis='y', linestyle='--', alpha=0.5)
                        
                        memfile = BytesIO()
                        plt.savefig(memfile, format='png', dpi=100)
                        plt.close(fig) # Memory leak önlemi
                        
                        doc.add_picture(memfile, width=Inches(5.5))
                        memfile.close()
                        doc.add_paragraph("Grafik 1: Ürünlerin fiyat değişim oranlarına göre dağılımı.")
                        doc.add_paragraph("")

                if 'Grup' in df_analiz.columns and 'Agirlik_2025' in df_analiz.columns and 'Fark' in df_analiz.columns:
                    df_analiz['Agirlik_2025'] = pd.to_numeric(df_analiz['Agirlik_2025'], errors='coerce').fillna(0)
                    df_analiz['Fark'] = pd.to_numeric(df_analiz['Fark'], errors='coerce').fillna(0)
                    
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
                        plt.close(fig) # Memory leak önlemi
                        
                        doc.add_picture(memfile2, width=Inches(6.0))
                        memfile2.close()
                        doc.add_paragraph("Grafik 2: Genel endeks üzerinde en çok baskı oluşturan ana harcama grupları.")

            except Exception as e:
                doc.add_paragraph(f"[Grafik oluşturulurken teknik bir sorun oluştu: {str(e)}]")
                plt.close('all')

        section = doc.sections[0]
        footer = section.footer
        p_foot = footer.paragraphs[0]
        p_foot.text = "Validasyon Müdürlüğü © 2026 - Gizli Belge"
        p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER

        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        # Hata durumunda boş ama geçerli bir dosya dön
        error_doc = Document()
        error_doc.add_heading('HATA RAPORU', 0)
        error_doc.add_paragraph(f"Rapor oluşturulurken bir hata meydana geldi: {str(e)}")
        err_buffer = BytesIO()
        error_doc.save(err_buffer)
        err_buffer.seek(0)
        return err_buffer

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

def stream_text(text, container, kutu_rengi, kenar_rengi, durum_emoji, durum_baslik, delay=0.015):
    for i in range(len(text) + 1):
        curr_text = text[:i]
        container.markdown(f"""
        <div class="delay-2 animate-enter" style="
            background: {kutu_rengi}; 
            border-left: 4px solid {kenar_rengi}; 
            border-radius: 12px; 
            padding: 24px; 
            margin-bottom: 30px;
            border-top: 1px solid rgba(255,255,255,0.05);
            border-right: 1px solid rgba(255,255,255,0.05);
            border-bottom: 1px solid rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
                <span style="font-size:24px;">{durum_emoji}</span>
                <span style="font-weight:700; color:#fff; letter-spacing:1px; font-size:14px; font-family:'Inter', sans-serif;">AI MARKET ANALİSTİ: <span style="color:{kenar_rengi}">{durum_baslik}</span> <span class="blink">|</span></span>
            </div>
            <div style="font-size:14px; color:#d4d4d8; line-height:1.6; font-style:italic; padding-left:42px;">
                "{curr_text}"
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(delay)

def style_chart(fig, is_pdf=False, is_sunburst=False):
    if is_pdf:
        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
    else:
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

# --- 9. YENİ MODÜLER SİTE MİMARİSİ ---

# 1. ADIM: VERİ VE HESAPLAMA MOTORU (Arayüzden Bağımsız)
def veri_motoru_calistir():
    """
    Veriyi çeker, işler ve Arayüz için gerekli istatistikleri hazırlar.
    """
    # Sidebar Ayarları
    st.sidebar.markdown("### ⚙️ Veri Ayarları")
    
    # Lottie (Opsiyonel)
    lottie_url = "https://lottie.host/98606416-297c-4a37-9b2a-714013063529/5D6o8k8fW0.json"
    try:
        lottie_json = load_lottieurl(lottie_url)
        with st.sidebar:
             if lottie_json: st_lottie(lottie_json, height=120, key="nav_anim")
    except: pass

    # Veri Çekme
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    
    if df_f.empty or df_s.empty:
        return None 

    # Tarih İşlemleri
    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
    raw_dates = df_f['Tarih_Str'].unique().tolist()
    
    # Başlangıç Tarihi Limiti
    BASLANGIC_LIMITI = "2026-02-04"
    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    
    if not tum_tarihler:
        st.sidebar.warning("Veri henüz oluşmadı.")
        return None

    secilen_tarih = st.sidebar.selectbox("Rapor Tarihi:", options=tum_tarihler, index=0)
    
    # --- YENİ EKLENEN KISIM: TRADINGVIEW SIDEBAR ---
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 Piyasalar")
    
    symbols = [
        {"s": "FX_IDC:USDTRY", "d": "Dolar / TL"},
        {"s": "FX_IDC:EURTRY", "d": "Euro / TL"},
        {"s": "FX_IDC:XAUTRYG", "d": "Gram Altın"},
        {"s": "TVC:UKOIL", "d": "Brent Petrol"},
        {"s": "BINANCE:BTCUSDT", "d": "Bitcoin ($)"}
    ]
    
    # Dikey yığınlama
    for sym in symbols:
        widget_code = f"""
        <div class="tradingview-widget-container" style="border-radius:12px; overflow:hidden; margin-bottom:10px;">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
          {{
          "symbol": "{sym['s']}",
          "width": "100%",
          "height": 100,
          "locale": "tr",
          "dateRange": "1D",
          "colorTheme": "dark",
          "isTransparent": true,
          "autosize": true,
          "largeChartUrl": ""
        }}
          </script>
        </div>
        """
        st.sidebar.components.v1.html(widget_code, height=110)
    # ---------------------------------------------
    
    # --- İŞLEME ---
    df_s.columns = df_s.columns.str.strip()
    kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
    ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
    col_w25, col_w26 = 'Agirlik_2025', 'Agirlik_2026'
    
    df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
    df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
    df_s = df_s.drop_duplicates(subset=['Kod'], keep='first')
    
    df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
    df_f = df_f[df_f['Fiyat'] > 0]
    
    # Pivot
    pivot = df_f.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat', aggfunc='mean')
    pivot = pivot.ffill(axis=1).bfill(axis=1).reset_index()
    
    if pivot.empty: return None

    # Grup Eşleştirme
    if 'Grup' not in df_s.columns:
        grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut",
                    "05": "Ev Eşyası", "06": "Sağlık", "07": "Ulaşım", "08": "Haberleşme", 
                    "09": "Eğlence", "10": "Eğitim", "11": "Lokanta", "12": "Çeşitli"}
        df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")

    df_analiz = pd.merge(df_s, pivot, on='Kod', how='left')
    tum_gunler_sirali = sorted([c for c in pivot.columns if c != 'Kod' and c >= BASLANGIC_LIMITI])
    
    # Tarih Filtresi
    if secilen_tarih in tum_gunler_sirali:
        idx = tum_gunler_sirali.index(secilen_tarih)
        gunler = tum_gunler_sirali[:idx+1]
    else:
        gunler = tum_gunler_sirali

    if not gunler: return None

    # Sayısallaştırma
    for col in gunler: df_analiz[col] = pd.to_numeric(df_analiz[col], errors='coerce')
    son = gunler[-1]
    dt_son = datetime.strptime(son, '%Y-%m-%d')
    
    # Baz ve Endeks Mantığı
    ZINCIR_TARIHI = datetime(2026, 2, 4)
    if dt_son >= ZINCIR_TARIHI:
        aktif_agirlik_col = col_w26
        gunler_2026 = [c for c in tum_gunler_sirali if c >= "2026-01-01"]
        baz_col = gunler_2026[0] if gunler_2026 else gunler[0]
        if baz_col in df_analiz.columns: df_analiz[baz_col] = df_analiz[baz_col].fillna(df_analiz[son])
    else:
        aktif_agirlik_col = col_w25
        baz_col = gunler[0]
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

    # Enflasyon Hesaplamaları
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
    
    # Günlük Değişim
    gun_farki = 0
    if len(gunler) >= 2:
        onceki_gun = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki_gun].replace(0, np.nan)) - 1
    else:
        df_analiz['Gunluk_Degisim'] = 0
        onceki_gun = son

    # Ay Sonu Tahmini
    month_end_forecast = 0.0
    target_fixed = f"{dt_son.year}-{dt_son.month:02d}-31"
    fixed_cols = [c for c in tum_gunler_sirali if c.startswith(bu_ay_str) and c <= target_fixed]
    if fixed_cols and not gecerli_veri.empty:
        gecerli_veri['Fixed_Ort'] = gecerli_veri[fixed_cols].apply(geo_mean, axis=1)
        gecerli_t = gecerli_veri.dropna(subset=['Fixed_Ort'])
        if not gecerli_t.empty and gecerli_t[aktif_agirlik_col].sum() > 0:
             month_end_forecast = ((gecerli_t[aktif_agirlik_col] * (gecerli_t['Fixed_Ort']/gecerli_t[baz_col])).sum() / gecerli_t[aktif_agirlik_col].sum() * 100) - 100

    # Resmi Veri (TÜİK) - AYLIK DEĞİŞİM HESABI
    resmi_aylik_degisim = 0.0
    try:
        df_resmi, _ = get_official_inflation()
        if df_resmi is not None and not df_resmi.empty:
             df_resmi = df_resmi.sort_values('Tarih')
             # Son iki veriyi al
             if len(df_resmi) >= 2:
                 son_endeks = df_resmi.iloc[-1]['Resmi_TUFE']
                 onceki_endeks = df_resmi.iloc[-2]['Resmi_TUFE']
                 resmi_aylik_degisim = ((son_endeks / onceki_endeks) - 1) * 100
    except:
        resmi_aylik_degisim = 0.0

    # İSTATİSTİKLER (Ana Sayfa İçin)
    toplam_urun_sayisi = len(df_analiz)
    toplam_kategori_sayisi = df_analiz['Grup'].nunique()
    veri_noktasi_tahmini = toplam_urun_sayisi * len(tum_gunler_sirali)

    return {
        "df_analiz": df_analiz,
        "enf_genel": enf_genel,
        "enf_gida": enf_gida,
        "tahmin": month_end_forecast,
        "resmi_aylik_degisim": resmi_aylik_degisim,
        "son": son,
        "onceki_gun": onceki_gun,
        "gunler": gunler,
        "ad_col": ad_col,
        "agirlik_col": aktif_agirlik_col,
        "baz_col": baz_col,
        "gun_farki": gun_farki,
        # Ana sayfa istatistikleri
        "stats_urun": toplam_urun_sayisi,
        "stats_kategori": toplam_kategori_sayisi,
        "stats_veri_noktasi": veri_noktasi_tahmini
    }

# --- 2. ADIM: SAYFA GÖRÜNÜMLERİ ---

def sayfa_ana_sayfa(ctx):
    # Dinamik verileri context'ten alıyoruz
    urun_sayisi = ctx["stats_urun"] if ctx else "..."
    kategori_sayisi = ctx["stats_kategori"] if ctx else "..."
    veri_noktasi = ctx["stats_veri_noktasi"] if ctx else "..."

    st.markdown(f"""
    <div style="text-align:center; padding: 40px 20px;">
        <h1 style="font-size: 56px; font-weight: 800; margin-bottom: 20px; background: -webkit-linear-gradient(45deg, #3b82f6, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            Gerçek Enflasyonu Keşfedin
        </h1>
        <p style="font-size: 20px; color: #a1a1aa; max-width: 800px; margin: 0 auto; line-height: 1.6;">
            Türkiye'nin en kapsamlı yapay zeka destekli fiyat takip sistemi. <br>
            <strong>{kategori_sayisi}</strong> farklı kategorideki <strong>{urun_sayisi}</strong> ürünü anlık izliyor, resmi verilerle kıyaslıyoruz.
        </p>
        <br><br>
        <div style="display:flex; justify-content:center; gap:30px; flex-wrap:wrap;">
            <div class="kpi-card" style="width:250px; text-align:center; padding:30px;">
                <div style="font-size:42px; margin-bottom:10px;">📦</div>
                <div style="font-size:32px; font-weight:bold; color:#fff;">{urun_sayisi}</div>
                <div style="color:#a1a1aa; font-size:14px; font-weight:600;">TAKİP EDİLEN ÜRÜN</div>
            </div>
            <div class="kpi-card" style="width:250px; text-align:center; padding:30px;">
                <div style="font-size:42px; margin-bottom:10px;">📊</div>
                <div style="font-size:32px; font-weight:bold; color:#fff;">{kategori_sayisi}</div>
                <div style="color:#a1a1aa; font-size:14px; font-weight:600;">ANA KATEGORİ</div>
            </div>
            <div class="kpi-card" style="width:250px; text-align:center; padding:30px;">
                <div style="font-size:42px; margin-bottom:10px;">⚡</div>
                <div style="font-size:32px; font-weight:bold; color:#fff;">{veri_noktasi}+</div>
                <div style="color:#a1a1aa; font-size:14px; font-weight:600;">İŞLENEN VERİ NOKTASI</div>
            </div>
        </div>
        <br><br>
        <div style="background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.2); padding: 15px; border-radius: 12px; display: inline-block;">
            <span style="color: #60a5fa; font-weight: bold;">🚀 SİSTEM DURUMU:</span> 
            <span style="color: #d1d5db;">Veri botları aktif. Fiyatlar <strong>{datetime.now().strftime('%H:%M')}</strong> itibarıyla güncel.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def sayfa_piyasa_ozeti(ctx):
    # KPI Kartları
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">GENEL ENFLASYON</div><div class="kpi-value">%{ctx["enf_genel"]:.2f}</div><div class="kpi-sub" style="color:#ef4444">Aylık Değişim</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">GIDA ENFLASYONU</div><div class="kpi-value">%{ctx["enf_gida"]:.2f}</div><div class="kpi-sub" style="color:#fca5a5">Mutfak Sepeti</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">AY SONU BEKLENTİ</div><div class="kpi-value">%{ctx["tahmin"]:.2f}</div><div class="kpi-sub" style="color:#a78bfa">AI Projeksiyonu</div></div>', unsafe_allow_html=True)
    with c4:
        # TÜİK Verisi (Artık Değişim Oranı)
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">RESMİ (TÜİK) VERİSİ</div><div class="kpi-value">%{ctx["resmi_aylik_degisim"]:.2f}</div><div class="kpi-sub" style="color:#fbbf24">Son Açıklanan Aylık</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Haber Bandı
    df = ctx["df_analiz"]
    inc = df.sort_values('Gunluk_Degisim', ascending=False).head(5)
    dec = df.sort_values('Gunluk_Degisim', ascending=True).head(5)
    items = []
    for _, r in inc.iterrows():
        if r['Gunluk_Degisim'] > 0: items.append(f"<span style='color:#f87171'>▲ {r[ctx['ad_col']]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    for _, r in dec.iterrows():
        if r['Gunluk_Degisim'] < 0: items.append(f"<span style='color:#34d399'>▼ {r[ctx['ad_col']]} %{r['Gunluk_Degisim']*100:.1f}</span>")
    ticker_html = " &nbsp;&nbsp; • &nbsp;&nbsp; ".join(items)
    st.markdown(f"""<div class="ticker-wrap"><div class="ticker-move">{ticker_html}</div></div>""", unsafe_allow_html=True)
    
    # GRAFİKLER
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        # --- HISTOGRAM ---
        fig_hist = px.histogram(
            df,
            x="Fark_Yuzde",
            nbins=20,
            title="Fiyat Değişim Dağılımı",
            color_discrete_sequence=["#3b82f6"]
        )
    
        fig_hist.update_layout(
            bargap=0.1
        )
    
        # --- X EKSENİ TAMAMEN KAPALI ---
        fig_hist.update_xaxes(
            title_text=None,        # Başlık yok
            showticklabels=False,   # Sayılar yok
            ticks="",               # Tick çizgileri yok
            showgrid=False,         # Grid yok
            visible=False           # Eksen komple yok
        )
    
        st.plotly_chart(
            style_chart(fig_hist),
            use_container_width=True,
            key="ozet_histogram"
        )


    with col_g2:
        rising = len(df[df['Fark'] > 0])
        falling = len(df[df['Fark'] < 0])
        st.markdown(f"""
        <div class="smart-card">
            <div class="sc-title">YÜKSELENLER</div>
            <div class="sc-val" style="color:#ef4444">{rising} Ürün</div>
            <div style="font-size:11px; color:#71717a;">Enflasyonist baskı</div>
        </div>
        <div class="smart-card" style="margin-top:10px;">
            <div class="sc-title">DÜŞENLER</div>
            <div class="sc-val" style="color:#10b981">{falling} Ürün</div>
            <div style="font-size:11px; color:#71717a;">Deflasyonist etki</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.subheader("Sektörel Isı Haritası")
    fig_tree = px.treemap(df, path=[px.Constant("Piyasa"), 'Grup', ctx['ad_col']], 
                          values=ctx['agirlik_col'], color='Fark', color_continuous_scale='RdYlGn_r')
    
    st.plotly_chart(style_chart(fig_tree, is_sunburst=True), use_container_width=True, key="ozet_treemap")

def sayfa_kategori_detay(ctx):
    df = ctx["df_analiz"]
    st.markdown("### 🔍 Kategori Bazlı Fiyat Takibi")
    
    col_sel, col_src = st.columns([1, 2])
    kategoriler = ["Tümü"] + sorted(df['Grup'].unique().tolist())
    secilen_kat = col_sel.selectbox("Kategori Seç:", kategoriler)
    arama = col_src.text_input("Ürün Ara:", placeholder="Örn: Süt, Yumurta...")
    
    df_show = df.copy()
    if secilen_kat != "Tümü":
        df_show = df_show[df_show['Grup'] == secilen_kat]
    if arama:
        df_show = df_show[df_show[ctx['ad_col']].astype(str).str.contains(arama, case=False, na=False)]
        
    if not df_show.empty:
        cols = st.columns(4)
        for idx, row in enumerate(df_show.to_dict('records')):
            fiyat = row[ctx['son']]
            fark = row.get('Gunluk_Degisim', 0) * 100
            cls = "pg-red" if fark > 0 else ("pg-green" if fark < 0 else "pg-yellow")
            icon = "▲" if fark > 0 else ("▼" if fark < 0 else "-")
            
            with cols[idx % 4]:
                st.markdown(f"""
                <div class="pg-card">
                    <div class="pg-name">{row[ctx['ad_col']]}</div>
                    <div class="pg-price">{fiyat:.2f} ₺</div>
                    <div class="pg-badge {cls}">{icon} %{fark:.2f}</div>
                </div>
                <div style="margin-bottom:15px;"></div>
                """, unsafe_allow_html=True)
    else:
        st.info("Kriterlere uygun ürün bulunamadı.")

def sayfa_tam_liste(ctx):
    st.markdown("### 📋 Detaylı Veri Seti")
    df = ctx["df_analiz"]
    
    def fix_sparkline(row):
        vals = row.tolist()
        if vals and min(vals) == max(vals): vals[-1] += 0.00001
        return vals
    
    df['Fiyat_Trendi'] = df[ctx['gunler']].apply(fix_sparkline, axis=1)
    
    cols_show = ['Grup', ctx['ad_col'], 'Fiyat_Trendi', ctx['baz_col'], 'Gunluk_Degisim']
    if ctx['baz_col'] != ctx['son']: cols_show.insert(3, ctx['son'])
    
    cfg = {
        "Fiyat_Trendi": st.column_config.LineChartColumn("Trend", width="small", y_min=0),
        ctx['ad_col']: "Ürün Adı",
        "Gunluk_Degisim": st.column_config.ProgressColumn("Değişim", format="%.2f%%", min_value=-0.5, max_value=0.5),
        ctx['baz_col']: st.column_config.NumberColumn(f"Baz Fiyat", format="%.2f ₺"),
        ctx['son']: st.column_config.NumberColumn(f"Son Fiyat", format="%.2f ₺")
    }
    
    st.data_editor(df[cols_show], column_config=cfg, hide_index=True, use_container_width=True, height=600)
    
    # Excel İndir
    output = BytesIO()
    with pd.ExcelWriter(output) as writer: df.to_excel(writer, index=False)
    st.download_button("📥 Excel Olarak İndir", data=output.getvalue(), file_name="Veri_Seti.xlsx")

def sayfa_raporlama(ctx):
    st.markdown("### 📝 Stratejik Pazar Raporu")
    
    rap_text = generate_detailed_static_report(
        df_analiz=ctx["df_analiz"], tarih=ctx["son"],
        enf_genel=ctx["enf_genel"], enf_gida=ctx["enf_gida"],
        gun_farki=ctx["gun_farki"], tahmin=ctx["tahmin"],
        ad_col=ctx["ad_col"], agirlik_col=ctx["agirlik_col"]
    )
    
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); padding:30px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); font-family:'Inter'; line-height:1.8;">
        {rap_text.replace(chr(10), '<br>').replace('**', '<b>').replace('**', '</b>')}
    </div>
    """, unsafe_allow_html=True)
    
    word_buffer = create_word_report(rap_text, ctx["son"], ctx["df_analiz"])
    st.download_button(
        label="📥 Word Raporu İndir", 
        data=word_buffer, 
        file_name="Strateji_Raporu.docx", 
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary"
    )

def sayfa_metodoloji():
    html_content = """
<style>
/* === CSS STİLLERİ === */
.methodology-container {
    font-family: 'Inter', sans-serif;
    color: #e4e4e7;
    max-width: 900px;
    margin: 0 auto;
}

/* ANA KART YAPISI */
.method-card {
    background: rgba(26, 28, 35, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 25px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

/* BAŞLIKLAR */
h1.main-title {
    font-size: 32px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 40px;
    background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

h2.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-top: 0;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}

h3.sub-title {
    font-size: 18px;
    font-weight: 600;
    color: #e2e8f0;
    margin-top: 20px;
    margin-bottom: 10px;
    display: inline-block;
    border-left: 3px solid #fbbf24;
    padding-left: 10px;
}

/* RENK TEMALARI */
.theme-blue h2 { color: #60a5fa; border-bottom-color: rgba(96, 165, 250, 0.3); }
.theme-purple h2 { color: #a78bfa; border-bottom-color: rgba(167, 139, 250, 0.3); }
.theme-yellow h2 { color: #fbbf24; border-bottom-color: rgba(251, 191, 36, 0.3); }
.theme-green h2 { color: #34d399; border-bottom-color: rgba(52, 211, 153, 0.3); }
.theme-gray h2 { color: #94a3b8; }

/* LİSTELER VE METİN */
p { font-size: 16px; line-height: 1.6; color: #cbd5e1; margin-bottom: 15px; }

ul.styled-list { list-style: none; padding: 0; margin: 15px 0; }
ul.styled-list li { position: relative; padding-left: 25px; margin-bottom: 10px; color: #d1d5db; }
ul.styled-list li::before { content: "➤"; position: absolute; left: 0; top: 2px; font-size: 12px; opacity: 0.7; }

.theme-blue ul li::before { color: #60a5fa; }
.theme-purple ul li::before { color: #a78bfa; }
.theme-yellow ul li::before { color: #fbbf24; }
.theme-green ul li::before { color: #34d399; }
.theme-gray ul li::before { color: #94a3b8; }

/* FORMÜL KUTUSU */
.formula-box {
    background: rgba(0, 0, 0, 0.3);
    border: 1px dashed rgba(251, 191, 36, 0.4);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 20px 0;
    color: #fbbf24;
    font-family: 'Courier New', monospace;
    font-size: 18px;
    font-weight: bold;
}
.formula-desc {
    font-size: 14px;
    color: #9ca3af;
    text-align: center;
    font-style: italic;
}
</style>

<section id="metodoloji" class="methodology-container theme-blue">

  <h1 class="main-title">Metodoloji ve Akademik Çerçeve</h1>

  <p>
    Piyasa Monitörü, Türkiye’de faaliyet gösteren zincir marketler ve e-ticaret platformları üzerinden
    yüksek frekanslı fiyat verisi toplayarak tüketici fiyatlarındaki değişimi gerçek zamanlıya yakın
    bir yaklaşımla izlemeyi amaçlayan alternatif bir fiyat endeksidir.
    Bu metodoloji, uluslararası istatistik standartları ve TÜİK fiyat endeksi prensipleri ile uyumlu
    olacak şekilde tasarlanmıştır.
  </p>

  <h2 class="section-title">1. Veri Toplama (Web Scraping)</h2>

  <p>
    Fiyat verileri, Python tabanlı web scraping altyapısı aracılığıyla günlük bazda otomatik olarak
    toplanmaktadır. Süreçte hem veri sürekliliği hem de kaynak platformların operasyonel
    sürdürülebilirliği gözetilmektedir.
  </p>

  <ul class="styled-list">
    <li>User-Agent rotasyonu uygulanır.</li>
    <li>Rate limiting mekanizması kullanılır.</li>
    <li>Platformlara aşırı yük bindirilmez.</li>
    <li>IP bazlı anomali tespiti yapılır.</li>
    <li>Eksik günler için veri boşlukları işaretlenir.</li>
  </ul>

  <h2 class="section-title">2. Veri Temizleme ve Ön İşleme</h2>

  <p>
    Toplanan ham fiyat verileri, endeks hesaplamasına dahil edilmeden önce çok aşamalı bir
    veri temizleme ve ön işleme sürecinden geçirilir. Amaç, ölçüm hatalarını ve geçici fiyat
    bozulmalarını minimize etmektir.
  </p>

  <ul class="styled-list">
    <li>Aykırı fiyat gözlemleri istatistiksel eşiklerle filtrelenir.</li>
    <li>Ürün gramaj ve ambalaj değişimleri normalize edilir.</li>
    <li>Stok dışı ürünler geçici olarak endeks dışı bırakılır.</li>
    <li>Yanlış eşleşen ürün tanımları otomatik olarak elenir.</li>
  </ul>

  <h2 class="section-title">3. Endeks Hesaplama Metodolojisi</h2>

  <p>
    Fiyat endeksi hesaplamasında zincirleme Laspeyres yaklaşımı benimsenmiştir.
    Bu yöntem, tüketim sepetinin zaman içerisinde güncellenmesine olanak tanırken,
    fiyat değişimlerinin karşılaştırılabilirliğini korur.
  </p>

  <div class="formula-box">
    I<sub>t</sub> = Σ ( P<sub>i,t</sub> / P<sub>i,0</sub> ) × W<sub>i</sub>
  </div>

  <div class="formula-desc">
    Zincirleme Laspeyres Fiyat Endeksi formülü
  </div>

  <h2 class="section-title">4. Ağırlıklandırma Yapısı</h2>

  <p>
    Ürün ağırlıkları, TÜİK Hanehalkı Bütçe Anketi (HBA) harcama payları temel alınarak
    belirlenmektedir. Bu sayede endeks, ortalama tüketici davranışını temsil etme
    kabiliyetine sahip olur.
  </p>

  <ul class="styled-list">
    <li>Alt ürün grupları için sabit ağırlıklar kullanılır.</li>
    <li>Yıllık periyotlarla ağırlık güncellemesi yapılır.</li>
    <li>Aşırı oynak kalemler için yumuşatma katsayıları uygulanır.</li>
  </ul>

  <h2 class="section-title">5. Kalite Kontrol ve Tutarlılık Analizi</h2>

  <p>
    Endeks çıktıları, hem zaman serisi tutarlılığı hem de resmi istatistiklerle
    karşılaştırmalı analizler yoluyla sürekli olarak izlenir.
  </p>

  <ul class="styled-list">
    <li>Günlük ve haftalık volatilite analizleri yapılır.</li>
    <li>TÜFE alt grupları ile korelasyonlar takip edilir.</li>
    <li>Metodoloji değişiklikleri geriye dönük olarak test edilir.</li>
  </ul>

  <h2 class="section-title">6. Akademik ve Politik Kullanım Alanları</h2>

  <p>
    Piyasa Monitörü Endeksi, akademik araştırmalar, para politikası analizleri ve
    erken enflasyon sinyali üretimi gibi alanlarda tamamlayıcı bir gösterge
    olarak kullanılabilecek şekilde tasarlanmıştır.
  </p>

</section>
"""
    st.markdown(html_content, unsafe_allow_html=True)


# --- ANA YÖNLENDİRİCİ ---

def main():
    # --- YENİ HEADER TASARIMI (COMPACT) ---
    st.markdown("""
        <style>
            .monitor-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 15px 25px; /* Daha az boşluk */
                background: linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%);
                border-bottom: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                margin-bottom: 20px;
                margin-top: -30px; /* Yukarıya daha da yaklaştır */
            }
            .mh-left {
                display: flex;
                flex-direction: column;
            }
            .mh-title {
                font-family: 'Inter', sans-serif;
                font-weight: 800;
                font-size: 24px; /* Font küçüldü */
                color: #fff;
                letter-spacing: -0.5px;
                line-height: 1.1;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .mh-badge {
                background: rgba(16, 185, 129, 0.15);
                color: #34d399;
                font-size: 10px;
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid rgba(16, 185, 129, 0.2);
                letter-spacing: 0.5px;
                font-weight: 700;
                vertical-align: middle;
            }
            .mh-subtitle {
                font-size: 12px;
                color: #94a3b8;
                margin-top: 2px;
                font-weight: 400;
            }
            .mh-right {
                text-align: right;
            }
            .mh-location {
                font-size: 10px;
                color: #64748b;
                font-weight: 700;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin-bottom: 2px;
            }
            .mh-date {
                font-size: 20px; /* Font küçüldü */
                font-weight: 700;
                color: #e2e8f0;
                font-family: 'JetBrains Mono', monospace;
            }
        </style>

        <div class="monitor-header">
            <div class="mh-left">
                <div class="mh-title">
                    Piyasa Monitörü
                    <span class="mh-badge">SİMÜLASYON</span>
                </div>
                <div class="mh-subtitle">Yapay Zeka Destekli Enflasyon Analiz Platformu</div>
            </div>
            <div class="mh-right">
                <div class="mh-location">İSTANBUL</div>
                <div class="mh-date">""" + datetime.now().strftime("%d.%m.%Y") + """</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # --- SENKRONİZASYON BUTONU (EKLENDİ) ---
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn2:
        if st.button("SİSTEMİ SENKRONİZE ET ⚡", type="primary", use_container_width=True):
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
                st.balloons() 
                time.sleep(1)
                st.rerun()
            elif "Veri bulunamadı" in res:
                st.warning("⚠️ Yeni veri akışı yok.")
            else:
                st.error(res)
    # ---------------------------------------

    # 1. Önce Veriyi Yükle (Ana Sayfa İstatistikleri İçin Gerekli)
    with st.spinner("Piyasa verileri analiz ediliyor..."):
        ctx = veri_motoru_calistir()

    # 2. Menü (Sadeleştirildi)
    tabs = st.tabs([
        "🏠 ANA SAYFA", 
        "📊 PİYASA ÖZETİ", 
        "📂 KATEGORİ DETAY", 
        "📋 TAM LİSTE", 
        "📝 RAPORLAMA", 
        "📐 METODOLOJİ"
    ])

    # 3. Sayfaları Yükle
    with tabs[0]:
        sayfa_ana_sayfa(ctx) # Context'i buraya gönderiyoruz

    if ctx:
        with tabs[1]: sayfa_piyasa_ozeti(ctx)
        with tabs[2]: sayfa_kategori_detay(ctx)
        with tabs[3]: sayfa_tam_liste(ctx)
        with tabs[4]: sayfa_raporlama(ctx)
    else:
        err_msg = "<br><div style='text-align:center; padding:20px; background:rgba(255,0,0,0.1); border-radius:10px; color:#fff;'>⚠️ Veri seti yüklenemedi. Lütfen internet bağlantınızı kontrol edin veya yöneticiye başvurun.</div>"
        with tabs[1]: st.markdown(err_msg, unsafe_allow_html=True)
        with tabs[2]: st.markdown(err_msg, unsafe_allow_html=True)
        with tabs[3]: st.markdown(err_msg, unsafe_allow_html=True)
        with tabs[4]: st.markdown(err_msg, unsafe_allow_html=True)

    with tabs[5]:
        sayfa_metodoloji()

    # Footer
    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px; opacity:0.6;">VALIDASYON MUDURLUGU © 2026 - GİZLİ ANALİZ BELGESİ</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
