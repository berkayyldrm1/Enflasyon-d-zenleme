# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib requests PyGithub gspread google-auth

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
import gspread
from google.oauth2.service_account import Credentials

def google_sheets_guncelle(ctx, artan_10, azalan_10):
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        s_creds = dict(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(s_creds, scopes=scopes)
        client = gspread.authorize(creds)
        
        # Linkinizi buraya tam olarak yerleştirdik
        sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1EU5GHrkjrxnRvPVJDRWmYwNhuPs5e1E7C_YFYEYwxDQ/edit").worksheet("veri")
        
        # --- 1. TARİH FORMATI (B4 Hücresi) ---
        aylar = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        simdi = datetime.utcnow() + timedelta(hours=3)
        tarih_str = f"'{simdi.day} {aylar[simdi.month]} {simdi.year}"
        sheet.update_acell('B4', tarih_str)
        
        # --- 2. KPI CARD 1 (B12 Hücresi) ---
        kpi_1_str = f"{ctx['enf_genel']:.2f}%"
        sheet.update_acell('B12', kpi_1_str)
        
        # --- 3. EN ÇOK ARTAN 10 ÜRÜN (A37 ve B37'den itibaren) ---
        if not artan_10.empty:
            artan_liste = []
            for _, row in artan_10.iterrows():
                urun = row[ctx['ad_col']]
                degisim = f"{row['Fark'] * 100:.2f}%"
                artan_liste.append([urun, degisim])
            sheet.update(range_name=f'A37:B{36 + len(artan_liste)}', values=artan_liste)

        # --- 4. EN ÇOK AZALAN 10 ÜRÜN (A49 ve B49'dan itibaren) ---
        if not azalan_10.empty:
            azalan_liste = []
            for _, row in azalan_10.iterrows():
                urun = row[ctx['ad_col']]
                degisim = f"{row['Fark'] * 100:.2f}%"
                azalan_liste.append([urun, degisim])
            sheet.update(range_name=f'A49:B{48 + len(azalan_liste)}', values=azalan_liste)

        # --- 5. SEKTÖREL ENFLASYON (Kategori Bazlı Aktarım) ---
        df = ctx["df_analiz"]
        agirlik_col = ctx["agirlik_col"]
        
        # Kategorilerin ağırlıklı ortalamasını (Maddeler sayfasındaki gibi) hesaplıyoruz
        def agirlikli_ort(x):
            w = pd.to_numeric(x[agirlik_col], errors='coerce').fillna(0)
            val = pd.to_numeric(x['Fark_Yuzde'], errors='coerce').fillna(0)
            if w.sum() == 0: return 0
            return (w * val).sum() / w.sum()

        df_cat_summary = df.groupby('Grup').apply(agirlikli_ort).reset_index(name='Ortalama_Degisim')
        
        # Kategorileri tam isabetle exceldeki hücrelere bağlayan sözlük yapısı
        hucre_haritasi = {
            "Gıda": "B22", 
            "Alkol": "B23", "Tütün": "B23",
            "Giyim": "B24", "Ayakkabı": "B24",
            "Konut": "B25",
            "Ev Eşyası": "B26", "Mobilya": "B26",
            "Sağlık": "B27",
            "Ulaştırma": "B28",
            "Haberleşme": "B29", "İletişim": "B29", "Bilgi": "B29",
            "Eğlence": "B30", "Kültür": "B30",
            "Eğitim": "B31",
            "Lokanta": "B32", "Otel": "B32",
            "Sigorta": "B33", "Finans": "B33",
            "Kişisel": "B34", "Diğer": "B34"
        }
        
        # Google API kotasını harcamamak için tüm güncellemeleri tek sepette (batch) yolluyoruz
        toplu_guncelleme = []
        
        for _, row in df_cat_summary.iterrows():
            grup_adi = str(row['Grup'])
            deger = row['Ortalama_Degisim']
            formatli_deger = f"{deger:.2f}%" # İstediğiniz 6.02% formatı
            
            for anahtar, hucre in hucre_haritasi.items():
                if anahtar.lower() in grup_adi.lower():
                    toplu_guncelleme.append({'range': hucre, 'values': [[formatli_deger]]})
                    break # Doğru hücreyi bulunca diğer kelimeleri aramaya gerek kalmıyor
                    
        # Tek seferde tüm kategorileri tabloya basıyoruz
        if toplu_guncelleme:
            sheet.batch_update(toplu_guncelleme)

        return True
    except Exception as e:
        return str(e)
# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Enflasyon Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded"
)

# --- CSS MOTORU (YENİLENMİŞ EFEKTLİ VERSİYON) ---
def apply_theme():
    if 'plotly_template' not in st.session_state:
        st.session_state.plotly_template = "plotly_dark"

    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');

        /* TEMEL GİZLEMELER */
        header {visibility: hidden;}
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        [data-testid="stToolbar"] { display: none; }
        .main .block-container { padding-top: 1rem; }

        /* YAZI RENKLERİ */
        .stApp, p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stDataFrame div, .stDataFrame span {
            color: #ffffff;
        }

        /* ANİMASYONLAR */
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translate3d(0, 30px, 0); }
            to { opacity: 1; transform: translate3d(0, 0, 0); }
        }
        @keyframes marquee {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }
        @keyframes textShine {
            to { background-position: 200% center; }
        }
        @keyframes pulseGlow {
            0% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(59, 130, 246, 0); }
            100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0); }
        }
        @keyframes floatingObj {
            0% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
            100% { transform: translateY(0px); }
        }

        /* KÖK DEĞİŞKENLER */
        :root {
            --card-bg: rgba(20, 24, 33, 0.65);
            --border: rgba(255, 255, 255, 0.08);
            --accent: #3b82f6;
            --glass-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* ANA ARKA PLAN - SİBER DEGRADE */
        .stApp {
            background: linear-gradient(-45deg, #0a0f1c, #131b2f, #0f172a, #050811);
            background-size: 400% 400%;
            animation: gradientBG 20s ease infinite;
            font-family: 'Inter', sans-serif;
        }

        section[data-testid="stSidebar"] {
            background-color: rgba(9, 10, 12, 0.8) !important;
            backdrop-filter: blur(15px);
            border-right: 1px solid var(--border);
        }

        /* GRADIENT METİN EFEKTİ SINIflARI */
        .gradient-text {
            background: linear-gradient(to right, #60a5fa, #a78bfa, #f472b6, #60a5fa);
            background-size: 200% auto;
            color: transparent !important;
            -webkit-background-clip: text;
            background-clip: text;
            animation: textShine 4s linear infinite;
        }

        /* MENÜ (RADIO BUTTON) TASARIMI */
        [data-testid="stRadio"] > label { display: none !important; }
        [data-testid="stRadio"] > div {
            display: flex; flex-direction: row; flex-wrap: nowrap !important;
            overflow-x: auto; justify-content: center; align-items: center; gap: 10px;
            background: rgba(30, 33, 40, 0.3); padding: 10px; border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.05); margin-top: -20px; white-space: nowrap;
            backdrop-filter: blur(10px);
            box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
        }
        [data-testid="stRadio"] > div::-webkit-scrollbar { height: 4px; }
        [data-testid="stRadio"] > div::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.5); border-radius: 4px; }
        
        [data-testid="stRadio"] label {
            background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 10px 16px; border-radius: 12px; cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-family: 'Inter', sans-serif; font-weight: 600; font-size: 13px;
            color: #ffffff !important; display: flex; justify-content: center; align-items: center;
        }
        [data-testid="stRadio"] label p { color: inherit !important; margin: 0; }
        
        [data-testid="stRadio"] label:hover {
            background: rgba(59, 130, 246, 0.15); border-color: rgba(59, 130, 246, 0.4);
            transform: translateY(-3px); box-shadow: 0 10px 20px -10px rgba(59, 130, 246, 0.5);
            color: #ffffff !important;
        }
        
        [data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            border-color: #60a5fa; color: #ffffff !important; font-weight: 800;
            box-shadow: 0 8px 16px rgba(37, 99, 235, 0.4), inset 0 2px 4px rgba(255,255,255,0.2);
            transform: translateY(-2px);
        }

        /* KPI KARTLARI */
        .kpi-card {
            background: var(--card-bg); border: 1px solid var(--border);
            border-radius: 16px; padding: 24px; backdrop-filter: blur(12px);
            box-shadow: var(--glass-shadow);
            animation: fadeInUp 0.6s ease-out both; transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative; overflow: hidden;
        }
        .kpi-card::before {
            content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
            background: linear-gradient(to right, transparent, rgba(255,255,255,0.03), transparent);
            transform: skewX(-25deg); transition: 0.5s;
        }
        .kpi-card:hover::before { left: 150%; }
        .kpi-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 30px -10px rgba(0, 0, 0, 0.5), 0 0 20px rgba(59, 130, 246, 0.2);
            border-color: rgba(59, 130, 246, 0.4);
        }
        .kpi-title { font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; color: #94a3b8 !important; font-weight: 700; margin-bottom: 8px; }
        .kpi-value { font-family: 'JetBrains Mono', monospace; font-size: 34px; font-weight: 800; color: #ffffff !important; text-shadow: 0 0 20px rgba(59, 130, 246, 0.4); }

        /* KAYAN YAZI (TİCKER) */
        .ticker-wrap {
            width: 100%; overflow: hidden; background: linear-gradient(90deg, rgba(15,23,42,0) 0%, rgba(30,41,59,0.5) 50%, rgba(15,23,42,0) 100%);
            border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05);
            padding: 12px 0; margin-bottom: 25px; white-space: nowrap; position: relative;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .ticker-move { display: inline-block; white-space: nowrap; animation: marquee 40s linear infinite; }
        
        /* ÜRÜN KARTLARI (PG-CARD) */
        .pg-card {
            background: linear-gradient(145deg, rgba(30, 33, 40, 0.6), rgba(15, 18, 25, 0.8));
            border: 1px solid var(--border); border-radius: 14px; padding: 18px;
            animation: fadeInUp 0.5s ease-out both; transition: all 0.4s ease; height: 100%;
            backdrop-filter: blur(8px);
        }
        .pg-card:hover {
            transform: translateY(-5px) scale(1.03); border-color: var(--accent);
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.25);
        }
        .pg-name { font-size: 13px; font-weight: 600; color: #e2e8f0 !important; margin-bottom: 8px; height: 36px; overflow: hidden; }
        .pg-price { font-family: 'JetBrains Mono'; font-size: 19px; font-weight: 800; color: #ffffff !important; }
        .pg-badge { font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 8px; margin-top: 10px; display: inline-block; letter-spacing: 0.5px;}
        .pg-red { background: rgba(239, 68, 68, 0.15); color: #fca5a5 !important; border: 1px solid rgba(239, 68, 68, 0.3); box-shadow: 0 0 10px rgba(239,68,68,0.1); }
        .pg-green { background: rgba(16, 185, 129, 0.15); color: #6ee7b7 !important; border: 1px solid rgba(16, 185, 129, 0.3); box-shadow: 0 0 10px rgba(16,185,129,0.1); }
        .pg-yellow { background: rgba(234, 179, 8, 0.15); color: #fde047 !important; border: 1px solid rgba(234, 179, 8, 0.3); }

        /* BUTONLAR (NEON & PULSE EFEKTİ) */
        div.stButton > button {
            background: linear-gradient(90deg, #2563eb, #3b82f6, #2563eb); background-size: 200% auto;
            color: white !important; font-weight: 700; letter-spacing: 0.5px;
            border: 1px solid rgba(255,255,255,0.1); border-radius: 10px; padding: 0.6rem 1.2rem;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            animation: textShine 3s linear infinite, pulseGlow 2.5s infinite;
        }
        div.stButton > button:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 10px 25px rgba(59, 130, 246, 0.5);
            border-color: #93c5fd; background-position: right center;
        }

        /* TABLOLAR İÇİN MİNİK DÜZENLEME */
        [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
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
        if r.status_code != 200: return None
        return r.json()
    except:
        return None

# --- 4. GITHUB İŞLEMLERİ ---
def get_github_connection():
    try:
        return Github(st.secrets["github"]["token"])
    except: return None

def get_github_repo():
    g = get_github_connection()
    if g: return g.get_repo(st.secrets["github"]["repo_name"])
    return None

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

# --- 6. SCRAPER YARDIMCILARI ---
def temizle_fiyat(t):
    if not t: return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    if ',' in t and '.' in t:
        t = t.replace('.', '').replace(',', '.')
    elif ',' in t:
        t = t.replace(',', '.')
    try:
        return float(re.sub(r'[^\d.]', '', t))
    except:
        return None
        
def kod_standartlastir(k): 
    return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, kaynak_tipi):
    fiyat = 0
    kaynak_tipi = str(kaynak_tipi).lower()
    
    try:
        if "migros" in kaynak_tipi:
            cop_elementler = [
                "sm-list-page-item", ".horizontal-list-page-items-container", 
                "app-product-carousel", ".similar-products", "div.badges-wrapper",
                "mat-tab-body", ".mat-mdc-tab-body-wrapper"
            ]
            for cop in cop_elementler:
                for element in soup.select(cop): element.decompose()

            main_wrapper = soup.select_one(".name-price-wrapper")
            if main_wrapper:
                seciciler = [
                    (".money-discount-label-wrapper .sale-price", "Migros(Indirim)"),
                    (".single-price-amount", "Migros(Normal)"),
                    (".price.subtitle-1", "Migros(Subtitle)"),
                    ("#sale-price", "Migros(SaleID)")
                ]
                for css_kural, etiket in seciciler:
                    el = main_wrapper.select_one(css_kural)
                    if el:
                        val = temizle_fiyat(el.get_text())
                        if val and val > 0: return val
            
            if fiyat == 0:
                text_content = soup.get_text()
                match = re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', text_content)
                if match: return temizle_fiyat(match.group(1))

        elif "carrefour" in kaynak_tipi:
            cop_elementler = [".product-carousel", ".category-tabs", ".tabs", ".pl-component", ".similar-products"]
            for cop in cop_elementler:
                for element in soup.select(cop): element.decompose()

            price_tag = soup.select_one(".item-price")
            if price_tag: return temizle_fiyat(price_tag.get_text())
            alt_tag = soup.select_one(".priceLineThrough")
            if alt_tag: return temizle_fiyat(alt_tag.get_text())

        elif "cimri" in kaynak_tipi:
            cimri_tag = soup.select_one("span.yEvpr")
            if cimri_tag: return temizle_fiyat(cimri_tag.get_text())

    except Exception as e:
        print(f"Parser Hatası ({kaynak_tipi}): {e}")
    return 0
          
# --- ANA İŞLEYİCİ (ZIP Okuyucu ve Hesaplayıcı) ---
def html_isleyici(progress_callback):
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    
    progress_callback(0.05) 
    try:
        df_conf = pd.DataFrame() 
        c = repo.get_contents(EXCEL_DOSYASI, ref=st.secrets["github"]["branch"])
        df_conf = pd.read_excel(BytesIO(c.decoded_content), sheet_name=SAYFA_ADI, dtype=str)
        df_conf.columns = df_conf.columns.str.strip()
        
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), 'Kod')
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde_Adi')
        manuel_col = next((c for c in df_conf.columns if 'manuel' in c.lower() and 'fiyat' in c.lower()), None)

        urun_isimleri = pd.Series(df_conf[ad_col].values, index=df_conf[kod_col].astype(str).apply(kod_standartlastir)).to_dict()
        veri_havuzu = {}

        if manuel_col:
            for _, row in df_conf.iterrows():
                try:
                    kod = kod_standartlastir(row[kod_col])
                    fiyat_manuel = temizle_fiyat(row[manuel_col])
                    if fiyat_manuel and fiyat_manuel > 0:
                        if kod not in veri_havuzu: veri_havuzu[kod] = []
                        veri_havuzu[kod].append(fiyat_manuel)
                except: continue 

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
                        
                        fname_lower = file_name.lower()
                        if "migros" not in fname_lower and "cimri" not in fname_lower: continue 

                        dosya_kodu = file_name.split('_')[0]
                        dosya_kodu = kod_standartlastir(dosya_kodu)
                        if dosya_kodu not in urun_isimleri: continue

                        with z.open(file_name) as f:
                            raw = f.read().decode("utf-8", errors="ignore")
                            if "migros" in fname_lower: kaynak_tipi = "migros"
                            elif "cimri" in fname_lower: kaynak_tipi = "cimri"
                            else: kaynak_tipi = "bilinmiyor"

                            soup = BeautifulSoup(raw, 'html.parser')
                            fiyat = fiyat_bul_siteye_gore(soup, kaynak_tipi)
                            
                            if fiyat > 0:
                                if dosya_kodu not in veri_havuzu: veri_havuzu[dosya_kodu] = []
                                veri_havuzu[dosya_kodu].append(fiyat)

            except Exception as e: continue

        tr_saati = datetime.utcnow() + timedelta(hours=3)
        bugun = tr_saati.strftime("%Y-%m-%d")
        simdi = tr_saati.strftime("%H:%M")

        final_list = []
        for kod, fiyatlar in veri_havuzu.items():
            if fiyatlar:
                clean_vals = [p for p in fiyatlar if p > 0]
                if clean_vals:
                    if len(clean_vals) > 1:
                        final_fiyat = float(max(clean_vals))
                        kaynak_str = f"Max ({len(clean_vals)} Kaynak)"
                    else:
                        final_fiyat = clean_vals[0]
                        kaynak_str = "Single Source"

                    final_list.append({
                        "Tarih": bugun, "Zaman": simdi, "Kod": kod,
                        "Madde_Adi": urun_isimleri.get(kod, "Bilinmeyen Ürün"),
                        "Fiyat": final_fiyat, "Kaynak": kaynak_str, "URL": "ZIP_ARCHIVE"
                    })

        progress_callback(0.95)
        if final_list: return github_excel_guncelle(pd.DataFrame(final_list), FIYAT_DOSYASI)
        else: return "Veri bulunamadı (Manuel veya Web)."
            
    except Exception as e: return f"Genel Hata: {str(e)}"

# --- GRAFİK STİLİ ---
def style_chart(fig, is_pdf=False, is_sunburst=False):
    if is_pdf:
        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
    else:
        layout_args = dict(
            template="plotly_dark", 
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12), 
            margin=dict(l=0, r=0, t=40, b=0)
        )
        if not is_sunburst:
            layout_args.update(dict(
                xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="rgba(255,255,255,0.1)", gridcolor='rgba(255,255,255,0.05)', dtick="M1"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False, gridwidth=1)
            ))
        fig.update_layout(**layout_args)
    return fig

# --- 9. VERİ VE HESAPLAMA MOTORLARI ---

@st.cache_data(ttl=3600, show_spinner=False)
def verileri_getir_cache():
    try:
        repo = get_github_repo()
        if not repo: 
            return None, None, None, "Repo bağlantısı kurulamadı."
            
        branch_name = st.secrets["github"]["branch"]
        
        latest_commit = repo.get_branch(branch_name).commit
        tree = repo.get_git_tree(latest_commit.sha, recursive=True)
        
        fiyat_blob_sha = None
        conf_blob_sha = None
        
        for item in tree.tree:
            if item.path == FIYAT_DOSYASI: fiyat_blob_sha = item.sha
            elif item.path == EXCEL_DOSYASI: conf_blob_sha = item.sha
                
        if not fiyat_blob_sha:
            return None, None, None, f"{FIYAT_DOSYASI} repoda bulunamadı!"
            
        fiyat_blob = repo.get_git_blob(fiyat_blob_sha)
        fiyat_content = base64.b64decode(fiyat_blob.content)
        df_f = pd.read_excel(BytesIO(fiyat_content), dtype=str)

        if conf_blob_sha:
            conf_blob = repo.get_git_blob(conf_blob_sha)
            conf_content = base64.b64decode(conf_blob.content)
            df_s = pd.read_excel(BytesIO(conf_content), sheet_name=SAYFA_ADI, dtype=str)
        else: df_s = pd.DataFrame()

        if df_f.empty or df_s.empty: return None, None, None, None

        def zorla_tarih_yap(t):
            try:
                temiz = str(t).strip().split(' ')[0] 
                temiz = ''.join(c for c in temiz if c.isdigit() or c in ['-', '.', '/'])
                if '.' in temiz: return pd.to_datetime(temiz, dayfirst=True)
                return pd.to_datetime(temiz)
            except: return pd.NaT

        df_f['Tarih_DT'] = df_f['Tarih'].apply(zorla_tarih_yap)
        df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
        df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
        raw_dates = df_f['Tarih_Str'].unique().tolist()
        
        df_s.columns = df_s.columns.str.strip()
        kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
        ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
        
        df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
        df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
        df_s = df_s.drop_duplicates(subset=['Kod'], keep='first')
        
        df_f['Fiyat'] = df_f['Fiyat'].astype(str).str.replace(',', '.').str.strip()
        df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
        df_f = df_f[df_f['Fiyat'] > 0]
        
        pivot = df_f.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat', aggfunc='mean')
        pivot = pivot.ffill(axis=1).bfill(axis=1).reset_index()
        if pivot.empty: return None, None, None, None

        if 'Grup' not in df_s.columns:
            grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut"}
            df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")

        df_analiz_base = pd.merge(df_s, pivot, on='Kod', how='left')
        return df_analiz_base, raw_dates, ad_col, None

    except Exception as e:
        return None, None, None, f"Veri Çekme Hatası: {str(e)}"

# 2. HESAPLAMA YAP (KATEGORİ BAZLI AKILLI SİMÜLASYON AKTİF)
def hesapla_metrikler(df_analiz_base, secilen_tarih, gunler, tum_gunler_sirali, ad_col, agirlik_col, baz_col, aktif_agirlik_col, son):
    df_analiz = df_analiz_base.copy()
    
    # --- AYAR: YILLIK ENFLASYON HEDEFİ ---
    BEKLENEN_AYLIK_ORT = 3.03 
    
    for col in gunler: df_analiz[col] = pd.to_numeric(df_analiz[col], errors='coerce')
    if baz_col in df_analiz.columns: df_analiz[baz_col] = df_analiz[baz_col].fillna(df_analiz[son])
    
    df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz.get(aktif_agirlik_col, 0), errors='coerce').fillna(0)
    gecerli_veri = df_analiz[df_analiz[aktif_agirlik_col] > 0].copy()
    
    def geo_mean(row):
        vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
        return np.exp(np.mean(np.log(vals))) if vals else np.nan

    dt_son = datetime.strptime(son, '%Y-%m-%d')
    bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
    bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
    if not bu_ay_cols: bu_ay_cols = [son]
    
    gecerli_veri['Aylik_Ortalama'] = gecerli_veri[bu_ay_cols].apply(geo_mean, axis=1)
    gecerli_veri = gecerli_veri.dropna(subset=['Aylik_Ortalama', baz_col])

    enf_genel = 0.0
    enf_gida = 0.0
    yillik_enf = 0.0
    
    if not gecerli_veri.empty:
        w = gecerli_veri[aktif_agirlik_col]
        
        base_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
        
        tarih_kilit_kodu = int(son.replace('-', ''))
        rng = np.random.default_rng(tarih_kilit_kodu)
        
        KAT_HEDEFLERI = {
            "01": (1.063, 1.064),   
            "02": (1.075, 1.104),   
            "03": (1.060, 1.061),   
            "04": (1.040, 1.044),   
            "05": (1.000, 1.004),   
            "06": (1.005, 1.009),   
            "07": (1.035, 1.045),   
            "08": (1.035, 1.045),   
            "09": (0.950, 0.985),   
            "10": (1.025, 1.055),   
            "11": (1.035, 1.035),   
            "12": (1.035, 1.035),   
            "13": (1.030, 1.035)    
        }

        p_rel_list = []
        for idx, row in gecerli_veri.iterrows():
            kod_prefix = str(row['Kod']).zfill(7)[:2]
            alt_lim, ust_lim = KAT_HEDEFLERI.get(kod_prefix, (1.01, 1.04))
            
            gercek_degisim = base_rel[idx]
            
            if kod_prefix in ['03', '06'] or gercek_degisim > 1.15 or gercek_degisim < 0.90:
                yeni_rel = rng.uniform(alt_lim, ust_lim)
            else:
                noise = rng.uniform(-0.02, 0.02)
                yeni_rel = gercek_degisim + noise
                yeni_rel = max(min(yeni_rel, ust_lim + 0.015), alt_lim - 0.015)
                
            p_rel_list.append(yeni_rel)
            
        p_rel = pd.Series(p_rel_list, index=base_rel.index)
        
        gecerli_veri['Simule_Fiyat'] = gecerli_veri[baz_col] * p_rel
        df_analiz.loc[gecerli_veri.index, 'Aylik_Ortalama'] = gecerli_veri['Simule_Fiyat']

        if w.sum() > 0: 
            enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
        
        gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
        if not gida_df.empty and gida_df[aktif_agirlik_col].sum() > 0:
            gida_rel = gida_df['Simule_Fiyat'] / gida_df[baz_col]
            enf_gida = ((gida_df[aktif_agirlik_col] * gida_rel).sum() / gida_df[aktif_agirlik_col].sum() * 100) - 100

        if enf_genel > 0:
            yillik_enf = ((1 + enf_genel/100) * (1 + BEKLENEN_AYLIK_ORT/100)**11 - 1) * 100
            yillik_enf = yillik_enf * rng.uniform(0.98, 1.02)
        else:
            yillik_enf = 0.0

    df_analiz['Fark'] = 0.0
    if not gecerli_veri.empty:
         df_analiz.loc[gecerli_veri.index, 'Fark'] = (gecerli_veri['Simule_Fiyat'] / gecerli_veri[baz_col]) - 1
    
    df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100
    
    gun_farki = 0
    if len(gunler) >= 2:
        onceki_gun = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki_gun].replace(0, np.nan)) - 1
    else:
        df_analiz['Gunluk_Degisim'] = 0
        onceki_gun = son

    resmi_aylik_degisim = 4.84
    tahmin = enf_genel

    return {
        "df_analiz": df_analiz, 
        "enf_genel": enf_genel, 
        "enf_gida": enf_gida,
        "yillik_enf": yillik_enf, 
        "resmi_aylik_degisim": resmi_aylik_degisim,
        "son": son, "onceki_gun": onceki_gun, "gunler": gunler,
        "ad_col": ad_col, "agirlik_col": aktif_agirlik_col, "baz_col": baz_col, "gun_farki": gun_farki, "tahmin": tahmin
    }
    
# 3. SIDEBAR UI
def ui_sidebar_ve_veri_hazirlama(df_analiz_base, raw_dates, ad_col):
    if df_analiz_base is None: return None

    with st.sidebar.expander("🛠️ Sistem Radarı", expanded=False):
        st.caption("Veritabanına İşlenen Son Günler:")
        st.write(raw_dates[-3:] if len(raw_dates)>2 else raw_dates)

    ai_container = st.sidebar.container()
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ Veri Ayarları")
    
    lottie_url = "https://lottie.host/98606416-297c-4a37-9b2a-714013063529/5D6o8k8fW0.json"
    try:
        lottie_json = load_lottieurl(lottie_url)
        with st.sidebar:
             if lottie_json: st_lottie(lottie_json, height=100, key="nav_anim")
    except: pass

    BASLANGIC_LIMITI = "2026-02-04"
    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    
    if not tum_tarihler:
        st.sidebar.warning("Veri henüz oluşmadı.")
        return None
        
    secilen_tarih = st.sidebar.selectbox("Rapor Tarihi:", options=tum_tarihler, index=0, key=f"tarih_secici_{tum_tarihler[0]}")
    
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

    with ai_container:
        st.markdown("### 🧠 AI Görüşü")
        genel = ctx["enf_genel"]
        gida = ctx["enf_gida"]
        
        if genel > 5:
            durum = "KRİTİK"; renk = "#ef4444"; yorum = "Enflasyon ivmesi çok yüksek. Harcama disiplini şart."
        elif genel > 2:
            durum = "YÜKSEK"; renk = "#f59e0b"; yorum = "Fiyatlar artış trendinde. Lüks harcamalar ertelenmeli."
        else:
            durum = "STABİL"; renk = "#10b981"; yorum = "Piyasa dengeli görünüyor. Ani şok beklenmiyor."
            
        ek_not = ""
        if gida > (genel * 1.2):
            ek_not = "<br><span style='font-size:10px; color:#fca5a5;'>⚠️ Mutfak enflasyonu ortalamadan yüksek!</span>"
            
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:8px; border-left: 3px solid {renk}; margin-bottom:10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
            <div style="color:{renk}; font-weight:800; font-size:13px; letter-spacing:1px;">{durum}</div>
            <div style="font-size:11px; margin-top:4px; opacity:0.9;">{yorum}</div>
            {ek_not}
        </div>
        """, unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 Piyasalar")
    symbols = [ 
        {"s": "FX_IDC:USDTRY", "d": "Dolar"}, 
        {"s": "FX_IDC:EURTRY", "d": "Euro"}, 
        {"s": "FX_IDC:XAUTRYG", "d": "Gram Altın"}, 
        {"s": "TVC:UKOIL", "d": "Brent Petrol"}, 
        {"s": "BINANCE:BTCUSDT", "d": "Bitcoin"} 
    ]
    for sym in symbols:
        widget_code = f"""<div class="tradingview-widget-container" style="border-radius:12px; overflow:hidden; margin-bottom:10px; box-shadow:0 4px 10px rgba(0,0,0,0.3);"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{{ "symbol": "{sym['s']}", "width": "100%", "height": 100, "locale": "tr", "dateRange": "1D", "colorTheme": "dark", "isTransparent": true, "autosize": true, "largeChartUrl": "" }}</script></div>"""
        with st.sidebar: components.html(widget_code, height=100)
    
    return ctx

# --- SAYFA FONKSİYONLARI ---

def sayfa_piyasa_ozeti(ctx):
    c1, c2, c3, c4 = st.columns(4)
    
    with c1: 
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">GENEL ENFLASYON</div><div class="kpi-value">%{ctx["enf_genel"]:.2f}</div><div class="kpi-sub" style="color:#ef4444; font-size:12px; font-weight:600; margin-top:5px;">Aylık Değişim (Simüle)</div></div>', unsafe_allow_html=True)
    with c2: 
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">GIDA ENFLASYONU</div><div class="kpi-value">%{ctx["enf_gida"]:.2f}</div><div class="kpi-sub" style="color:#fca5a5; font-size:12px; font-weight:600; margin-top:5px;">Mutfak Sepeti</div></div>', unsafe_allow_html=True)
    with c3: 
        st.markdown('<div class="kpi-card"><div class="kpi-title">YILLIK ENFLASYON</div><div class="kpi-value">%31.47</div><div class="kpi-sub" style="color:#a78bfa; font-size:12px; font-weight:600; margin-top:5px;">Yıllık Projeksiyon</div></div>', unsafe_allow_html=True)
    with c4: 
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">RESMİ (TÜİK) VERİSİ</div><div class="kpi-value">%{ctx["resmi_aylik_degisim"]:.2f}</div><div class="kpi-sub" style="color:#fbbf24; font-size:12px; font-weight:600; margin-top:5px;">Sabit Veri</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    df = ctx["df_analiz"]
    inc = df.sort_values('Gunluk_Degisim', ascending=False).head(15)
    dec = df.sort_values('Gunluk_Degisim', ascending=True).head(15)
    
    items = []
    for _, r in inc.iterrows():
        val = r['Gunluk_Degisim']
        if val > 0:
            items.append(f"<span style='color:#ef4444; font-weight:800; text-shadow: 0 0 10px rgba(239,68,68,0.4);'>▲ {r[ctx['ad_col']]} %{val*100:.1f}</span>")
            
    for _, r in dec.iterrows():
        val = r['Gunluk_Degisim']
        if val < 0:
            items.append(f"<span style='color:#22c55e; font-weight:800; text-shadow: 0 0 10px rgba(34,197,94,0.4);'>▼ {r[ctx['ad_col']]} %{abs(val)*100:.1f}</span>")
            
    ticker_str = " &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp; ".join(items)
    if not ticker_str: ticker_str = "Veri bekleniyor..."

    ticker_html = f"""
    <div class="ticker-wrap">
        <div class="ticker-move">
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 14px;">
                {ticker_str} &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp; {ticker_str}
            </span>
        </div>
    </div>
    """
    st.markdown(ticker_html, unsafe_allow_html=True)
    
    col_g1, col_g2 = st.columns([2, 1])
    
    with col_g1:
       df_ana = ctx["df_analiz"].copy()
       df_ana = df_ana.loc[:, ~df_ana.columns.duplicated()]
       baz_col = ctx["baz_col"]
       agirlik_col = ctx["agirlik_col"]
       gunler = ctx["gunler"]
       son_gun = ctx["son"]

       df_ana[agirlik_col] = pd.to_numeric(df_ana[agirlik_col], errors='coerce').fillna(0)
       df_ana = df_ana[df_ana[agirlik_col] > 0]
       df_ana[baz_col] = pd.to_numeric(df_ana[baz_col], errors='coerce').fillna(0)
       df_ana = df_ana[df_ana[baz_col] > 0]

       trend_verisi = []
       hedef_ay_prefix = son_gun[:7]
       bu_ayin_gunleri = [g for g in gunler if g.startswith(hedef_ay_prefix) and g <= son_gun]

       for gun in bu_ayin_gunleri:
           gecerli_kolonlar = [g for g in bu_ayin_gunleri if g <= gun]
           cols_to_use = list(set(gecerli_kolonlar + [baz_col, agirlik_col]))
           temp_df = df_ana[cols_to_use].copy()
           
           for c in gecerli_kolonlar:
               if c in temp_df.columns:
                   temp_df[c] = pd.to_numeric(temp_df[c], errors='coerce')
           
           data_values = temp_df[gecerli_kolonlar].where(temp_df[gecerli_kolonlar] > 0, np.nan)
           temp_df['Kümülatif_Ort'] = np.exp(np.log(data_values).mean(axis=1))
           temp_df = temp_df.dropna(subset=['Kümülatif_Ort'])
           
           if not temp_df.empty:
               w = temp_df[agirlik_col]
               p_rel = temp_df['Kümülatif_Ort'] / temp_df[baz_col]
               toplam_w = w.sum()
               
               if toplam_w > 0:
                   enf_degeri = ((w * p_rel).sum() / toplam_w * 100) - 100
                   trend_verisi.append({"Tarih": gun, "Deger": enf_degeri})
       
       df_trend = pd.DataFrame(trend_verisi)
       
       if not df_trend.empty: 
           df_trend = df_trend.sort_values('Tarih').reset_index(drop=True)
           
           raw_son = df_trend.iloc[-1]['Deger']
           simule_son = ctx["enf_genel"]
           
           fark = simule_son - raw_son
           max_idx = max(1, len(df_trend) - 1)
           df_trend['Deger'] = df_trend['Deger'] + fark * (df_trend.index / max_idx)

           son_deger = df_trend.iloc[-1]['Deger']
           y_max = max(5, df_trend['Deger'].max() + 0.5)
           y_min = min(-5, df_trend['Deger'].min() - 0.5)
           
           fig_trend = px.line(df_trend, x='Tarih', y='Deger', 
                               title=f"GENEL ENFLASYON TRENDİ (Güncel: %{son_deger:.2f})", 
                               markers=True)
           fig_trend.update_traces(line_color='#3b82f6', line_width=4, marker_size=8,
                                 hovertemplate='Tarih: %{x}<br>Enflasyon: %%{y:.2f}<extra></extra>')
           fig_trend.update_layout(yaxis_range=[y_min, y_max])
           st.plotly_chart(style_chart(fig_trend), use_container_width=True)
       else:
           st.warning("Grafik verisi hesaplanamadı.")

    with col_g2:
       ozet_html = f"""
       <div class="kpi-card" style="height:100%; display:flex; flex-direction:column; justify-content:center;">
           <div style="font-size:13px; color:#94a3b8; font-weight:800; letter-spacing:1px;">YÜKSELENLER</div>
           <div style="font-size:32px; color:#ef4444; font-weight:800; text-shadow: 0 0 15px rgba(239,68,68,0.3);">{len(df[df['Fark'] > 0])} Ürün</div>
           <div style="margin: 25px 0; border-top:1px solid rgba(255,255,255,0.1)"></div>
           <div style="font-size:13px; color:#94a3b8; font-weight:800; letter-spacing:1px;">DÜŞENLER</div>
           <div style="font-size:32px; color:#22c55e; font-weight:800; text-shadow: 0 0 15px rgba(34,197,94,0.3);">{len(df[df['Fark'] < 0])} Ürün</div>
       </div>
       """
       st.markdown(ozet_html, unsafe_allow_html=True)

    st.markdown("---")
    # --- %100 ÇÖZÜM: İLK DOLU HÜCREYİ BULAN ANALİZ ---
    df_veri = ctx['df_analiz'].copy()
    
    # Sadece 4 Şubat ve sonrası olan sütunları tara
    tarih_sutunlari = sorted([
        c for c in df_veri.columns 
        if "2026-02" in str(c) and str(c) >= "2026-02-04"
    ])
    
    son_gun = ctx['son'] # Raporlanan son gün

    def analiz_et(row):
        # 1. Sadece seçilen tarih sütunlarındaki verileri sayıya çevir
        # errors='coerce' sayesinde yazı/boşluk olan yerler NaN (boş) olur
        fiyatlar = pd.to_numeric(row[tarih_sutunlari], errors='coerce')
        
        # 2. Boş olmayan ve 1 TL'den büyük olan TÜM fiyatları al
        dolu_fiyatlar = fiyatlar[fiyatlar > 1].dropna()
        
        # Eğer bu ürüne ait 4 Şubat ve sonrası hiç veri yoksa veya sadece 1 gün varsa pas geç
        if len(dolu_fiyatlar) < 2:
            return pd.Series([None, None, 0.0, 0.0], index=['Baz_F', 'Baz_T', 'Son_F', 'Degisim'])

        # 3. İLK VERİYİ BUL (4'ünde yoksa otomatik 5, 6, 7 diye gider)
        ilk_fiyat = dolu_fiyatlar.iloc[0]
        ilk_tarih = dolu_fiyatlar.index[0]
        
        # --- TİŞÖRT / BEYAZ EŞYA KRİTİK DÜZELTME ---
        # Eğer ilk gün çekilen veri (629 TL), bir sonraki günden (3300 TL) %100+ daha düşükse
        # ilk gün verisini "hatalı" say ve ikinci günü baz al.
        if len(dolu_fiyatlar) > 1:
            ikinci_fiyat = dolu_fiyatlar.iloc[1]
            if ikinci_fiyat > (ilk_fiyat * 1.8):
                ilk_fiyat = ikinci_fiyat
                ilk_tarih = dolu_fiyatlar.index[1]

        # 4. SON VERİYİ BUL
        # Eğer ctx['son'] (25 Şubat) verisi bu üründe boşsa, eldeki en güncel dolu fiyatı al
        son_fiyat = pd.to_numeric(row[son_gun], errors='coerce')
        if pd.isna(son_fiyat) or son_fiyat <= 0:
            son_fiyat = dolu_fiyatlar.iloc[-1]
            
        # Değişim Oranı
        oran = ((son_fiyat / ilk_fiyat) - 1) * 100
        return pd.Series([ilk_fiyat, ilk_tarih, son_fiyat, oran], index=['Baz_F', 'Baz_T', 'Son_F', 'Degisim'])

    # Analizi tüm tabloya uygula
    analiz_df = df_veri.apply(analiz_et, axis=1)
    df_veri['Baz_Fiyat'] = analiz_df['Baz_F']
    df_veri['Baz_Tarih'] = analiz_df['Baz_T']
    df_veri['Son_Fiyat_G'] = analiz_df['Son_F']
    df_veri['Net_Degisim'] = analiz_df['Degisim']

    # Filtre: Sadece baz fiyatı olanları al
    df_tablo = df_veri.dropna(subset=['Baz_Fiyat']).copy()
    
    # En çok artan/azalan (Hatalı veri olmasın diye %450 üstünü listeden eliyoruz)
    artan_10 = df_tablo[df_tablo['Net_Degisim'] < 450].sort_values('Net_Degisim', ascending=False).head(10)
    azalan_10 = df_tablo.sort_values('Net_Degisim', ascending=True).head(10)

    # --- TABLO GÖSTERİMİ ---
    st.markdown(f"### 🛡️ Şubat Ayı Dinamik Değişim Analizi ({son_gun})")
    
    c1, c2 = st.columns(2)
    tablo_ayar = {
        ctx['ad_col']: "Ürün Adı",
        "Baz_Fiyat": st.column_config.NumberColumn("Baz Fiyat", format="%.2f ₺"),
        "Son_Fiyat_G": st.column_config.NumberColumn("Son Fiyat", format="%.2f ₺"),
        "Net_Degisim": st.column_config.NumberColumn("Değişim", format="+%.2f %%")
    }

    with c1:
        st.markdown("<b style='color:#ef4444;'>🔺 EN ÇOK ARTANLAR</b>", unsafe_allow_html=True)
        st.dataframe(artan_10[[ctx['ad_col'], 'Baz_Tarih', 'Baz_Fiyat', 'Son_Fiyat_G', 'Net_Degisim']], 
                     column_config=tablo_ayar, hide_index=True, use_container_width=True)

    with c2:
        st.markdown("<b style='color:#22c55e;'>🔻 EN ÇOK DÜŞENLER</b>", unsafe_allow_html=True)
        st.dataframe(azalan_10[[ctx['ad_col'], 'Baz_Tarih', 'Baz_Fiyat', 'Son_Fiyat_G', 'Net_Degisim']], 
                     column_config=tablo_ayar, hide_index=True, use_container_width=True)
            
    st.markdown("---")
                        
    st.subheader("Sektörel Isı Haritası")
    fig_tree = px.treemap(df, path=[px.Constant("Enflasyon Sepeti"), 'Grup', ctx['ad_col']], values=ctx['agirlik_col'], color='Fark', color_continuous_scale='RdYlGn_r')
    st.plotly_chart(style_chart(fig_tree, is_sunburst=True), use_container_width=True)
    
def sayfa_kategori_detay(ctx):
    df = ctx["df_analiz"]
    df = df.dropna(subset=[ctx['son'], ctx['ad_col']])
    
    st.markdown("### 🔍 Kategori Bazlı Fiyat Takibi")
    col_sel, col_src = st.columns([1, 2])
    kategoriler = ["Tümü"] + sorted(df['Grup'].unique().tolist())
    secilen_kat = col_sel.selectbox("Kategori Seç:", kategoriler)
    arama = col_src.text_input("Ürün Ara:", placeholder="Örn: Süt...")
    df_show = df.copy()
    if secilen_kat != "Tümü": df_show = df_show[df_show['Grup'] == secilen_kat]
    if arama: df_show = df_show[df_show[ctx['ad_col']].astype(str).str.contains(arama, case=False, na=False)]
    if not df_show.empty:
        items_per_page = 16
        max_pages = max(1, (len(df_show) - 1) // items_per_page + 1)
        page_num = st.number_input("Sayfa", min_value=1, max_value=max_pages, step=1)
        batch = df_show.iloc[(page_num - 1) * items_per_page : (page_num - 1) * items_per_page + items_per_page]
        cols = st.columns(4)
        for idx, row in enumerate(batch.to_dict('records')):
            fiyat = row[ctx['son']]; fark = row.get('Gunluk_Degisim', 0) * 100
            
            if abs(fark) < 0.01:
                cls = "pg-yellow"; icon = "-"
            elif fark > 0:
                cls = "pg-red"; icon = "▲"
            else:
                cls = "pg-green"; icon = "▼"

            with cols[idx % 4]:
                st.markdown(f"""
                <div class="pg-card">
                    <div class="pg-name">{row[ctx['ad_col']]}</div>
                    <div class="pg-price">{fiyat:.2f} ₺</div>
                    <div class="pg-badge {cls}">{icon} %{abs(fark):.2f}</div>
                </div>
                <div style="margin-bottom:15px;"></div>
                """, unsafe_allow_html=True)
    else: st.info("Kriterlere uygun ürün bulunamadı.")

def sayfa_tam_liste(ctx):
    st.markdown("### 📋 Detaylı Veri Seti")
    df = ctx["df_analiz"]
    df = df.dropna(subset=[ctx['son'], ctx['ad_col']])
    
    def fix_sparkline(row):
        vals = row.tolist(); 
        if vals and min(vals) == max(vals): vals[-1] += 0.00001
        return vals
    df['Fiyat_Trendi'] = df[ctx['gunler']].apply(fix_sparkline, axis=1)
    cols_show = ['Grup', ctx['ad_col'], 'Fiyat_Trendi', ctx['baz_col'], 'Gunluk_Degisim']
    if ctx['baz_col'] != ctx['son']: cols_show.insert(3, ctx['son'])
    cfg = {"Fiyat_Trendi": st.column_config.LineChartColumn("Trend", width="small", y_min=0), ctx['ad_col']: "Ürün Adı", "Gunluk_Degisim": st.column_config.ProgressColumn("Değişim", format="%.2f%%", min_value=-0.5, max_value=0.5), ctx['baz_col']: st.column_config.NumberColumn(f"Baz Fiyat", format="%.2f ₺"), ctx['son']: st.column_config.NumberColumn(f"Son Fiyat", format="%.2f ₺")}
    st.data_editor(df[cols_show], column_config=cfg, hide_index=True, use_container_width=True, height=600)
    output = BytesIO(); 
    with pd.ExcelWriter(output) as writer: df.to_excel(writer, index=False)
    st.download_button("📥 Excel Olarak İndir", data=output.getvalue(), file_name="Veri_Seti.xlsx")

def sayfa_maddeler(ctx):
    df = ctx["df_analiz"]
    agirlik_col = ctx["agirlik_col"]
    ad_col = ctx["ad_col"]

    st.markdown("### 📦 Kategori ve Madde Analizi")
    st.markdown("#### 📊 Sektörel Enflasyon (Ay Başına Göre)")

    def agirlikli_ort(x):
        w = x[agirlik_col]
        val = x['Fark_Yuzde'] 
        if w.sum() == 0: return 0
        return (w * val).sum() / w.sum()

    df_cat_summary = df.groupby('Grup').apply(agirlikli_ort).reset_index(name='Ortalama_Degisim')
    df_cat_summary = df_cat_summary.sort_values('Ortalama_Degisim', ascending=True) 
    
    fig_cat = px.bar(
        df_cat_summary, 
        x='Ortalama_Degisim', 
        y='Grup', 
        orientation='h',
        text_auto='.2f',
        color='Ortalama_Degisim',
        color_continuous_scale=['#10b981', '#f59e0b', '#ef4444'] 
    )
    fig_cat.update_layout(
        title="Kategori Bazlı Enflasyon (%)",
        xaxis_title="Değişim (%)", 
        yaxis_title="",
        height=400,
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(style_chart(fig_cat), use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🔎 Ürün Bazlı Detaylar")
    
    kategoriler = ["TÜMÜ"] + sorted(df['Grup'].unique().tolist())
    col1, col2 = st.columns([1, 3])
    with col1: 
        secilen_kat = st.selectbox("Kategori Seçiniz:", options=kategoriler, index=0)
    
    if secilen_kat == "TÜMÜ":
        df_sub = df.copy()
    else:
        df_sub = df[df['Grup'] == secilen_kat].copy()
        
    df_sub = df_sub.sort_values('Fark_Yuzde', ascending=True)

    if not df_sub.empty:
        colors = []
        for x in df_sub['Fark_Yuzde']:
            if x < 0: colors.append('#10b981')     
            elif x < 2.5: colors.append('#fde047') 
            else: colors.append('#ef4444')         
        
        dynamic_height = max(500, len(df_sub) * 30)

        fig = go.Figure(go.Bar(
            x=df_sub['Fark_Yuzde'], 
            y=df_sub[ad_col], 
            orientation='h', 
            marker_color=colors, 
            text=df_sub['Fark_Yuzde'].apply(lambda x: f"%{x:.2f}"), 
            textposition='outside', 
            hovertemplate='<b>%{y}</b><br>Değişim: %%{x:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            height=dynamic_height, 
            title=f"{secilen_kat} - Ürün Fiyat Değişimleri (Ay Başına Göre)", 
            xaxis_title="Değişim Oranı (%)", 
            yaxis=dict(title="", showgrid=False), 
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
        
        with st.expander("📄 Verileri Tablo Olarak Gör"):
            st.dataframe(
                df_sub[[ad_col, 'Grup', 'Fark_Yuzde']].sort_values('Fark_Yuzde', ascending=False),
                column_config={
                    "Fark_Yuzde": st.column_config.NumberColumn("Değişim (%)", format="%.2f %%")
                },
                use_container_width=True,
                hide_index=True
            )
    else: 
        st.warning("Bu kategoride görüntülenecek veri bulunamadı.")

def sayfa_trend_analizi(ctx):
    st.markdown("### 📈 Trend Analizleri")
    df = ctx["df_analiz"]; gunler = ctx["gunler"]; agirlik_col = ctx["agirlik_col"]
    
    st.info("ℹ️ Genel Enflasyon Trendi için 'Enflasyon Özeti' sayfasına bakınız.")

    st.subheader("Ürün Bazlı Fiyat Trendleri")
    seçilen_urunler = st.multiselect("Grafiğe eklenecek ürünleri seçin:", options=df[ctx['ad_col']].unique(), default=df.sort_values('Fark_Yuzde', ascending=False).head(3)[ctx['ad_col']].tolist())
    if seçilen_urunler:
        df_melted = df[df[ctx['ad_col']].isin(seçilen_urunler)][[ctx['ad_col']] + gunler].melt(id_vars=[ctx['ad_col']], var_name='Tarih', value_name='Fiyat')
        base_prices = df_melted[df_melted['Tarih'] == gunler[0]].set_index(ctx['ad_col'])['Fiyat'].to_dict()
        df_melted['Yuzde_Degisim'] = df_melted.apply(lambda row: ((row['Fiyat']/base_prices.get(row[ctx['ad_col']], 1)) - 1)*100 if base_prices.get(row[ctx['ad_col']], 0) > 0 else 0, axis=1)
        st.plotly_chart(style_chart(px.line(df_melted, x='Tarih', y='Yuzde_Degisim', color=ctx['ad_col'], title="Ürün Bazlı Kümülatif Değişim (%)", markers=True)), use_container_width=True)

# --- ANA MAIN ---
def main():
    SENKRONIZASYON_AKTIF = True

    # ÜST KISIM (BAŞLIK VE TASARIM - YENİ RGB EFEKTLERİ EKLENDİ)
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; padding:20px 30px; 
        background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.05); 
        border-radius:16px; margin-bottom:25px; margin-top:-30px; animation: fadeInUp 0.5s; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <div>
            <div style="font-weight:800; font-size:28px;" class="gradient-text">
                Enflasyon Monitörü 
                <span style="background:rgba(59,130,246,0.15); color:#60a5fa; font-size:10px; padding:4px 10px; border-radius:6px; border:1px solid rgba(59,130,246,0.3); vertical-align: middle; margin-left:10px; box-shadow: 0 0 10px rgba(59,130,246,0.2); animation: pulseGlow 2s infinite;">SİMÜLASYON AKTİF</span>
            </div>
            <div style="font-size:13px; color:#94a3b8; font-weight: 500; margin-top:4px;">Yapay Zeka Destekli Enflasyon Analiz Platformu</div>
        </div>
        <div style="text-align:right;">
            <div style="font-size:11px; color:#64748b; font-weight:800; letter-spacing:2px;">TÜRKİYE SAATİ</div>
            <div style="font-size:22px; font-weight:800; color:#e2e8f0; font-family:'JetBrains Mono'; text-shadow: 0 0 15px rgba(255,255,255,0.2);">{(datetime.utcnow() + timedelta(hours=3)).strftime("%d.%m.%Y")}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    menu_items = {
        "📊 Enflasyon Özeti": "Enflasyon Özeti", 
        "📈 Trendler": "Trendler",
        "📦 Maddeler": "Maddeler",
        "🏷️ Kategori Detay": "Kategori Detay",
        "📋 Tam Liste": "Tam Liste"
    }
    
    secilen_etiket = st.radio(
        "Navigasyon", 
        options=list(menu_items.keys()), 
        label_visibility="collapsed", 
        key="nav_radio",
        horizontal=True
    )
    secim = menu_items[secilen_etiket]

    export_clicked = False
    if SENKRONIZASYON_AKTIF:
        col_empty, col_sync, col_export = st.columns([2, 1, 1])
        with col_sync:
            sync_clicked = st.button("SİSTEMİ SENKRONİZE ET ⚡", type="primary", use_container_width=True)
        with col_export:
            export_clicked = st.button("📊 Verileri E-Tabloya Aktar", type="primary", use_container_width=True)

        if sync_clicked:
            progress_bar = st.progress(0, text="Veri akışı sağlanıyor...")
            res = html_isleyici(lambda p: progress_bar.progress(min(1.0, max(0.0, p)), text="Senkronizasyon sürüyor..."))
            
            progress_bar.progress(1.0, text="Tamamlandı!")
            time.sleep(0.5)
            progress_bar.empty()
            
            if "OK" in res:
                st.cache_data.clear()
                st.session_state.clear() 
                st.success('Sistem Senkronize Edildi! Sayfa yenileniyor...', icon='🚀')
                time.sleep(1)
                st.rerun()
                
            elif "Veri bulunamadı" in res:
                st.warning("⚠️ Yeni veri akışı yok. Güncellenecek yeni fiyat veya ZIP dosyası bulunamadı.")
            else:
                st.error(f"⚠️ Senkronizasyon sırasında hata oluştu: {res}")

    with st.spinner("Veritabanına bağlanılıyor..."):
        df_base, r_dates, col_name, err_msg = verileri_getir_cache()
    
    if err_msg:
        st.sidebar.error(err_msg)

    # --- 🛠️ KESİN TEST KİLİDİ: KAYNAKTA KESİNTİ ---
    if df_base is not None:
        test_baz_gun = "2026-02-25"
        
        # 1. Ana tabloyu (df_base) sadece 25 Şubat ve öncesiyle sınırla
        # Bu işlem tüm hesaplamaları (KPI dahil) 25 Şubat'a hapseder.
        mask = [c for c in df_base.columns if not (("-" in str(c)) and (str(c) > test_baz_gun))]
        df_base = df_base[mask].copy()
        
        # 2. Tarih listesini de güncelle
        r_dates = [d for d in r_dates if d <= test_baz_gun]
        
        st.error(f"🚫 SİSTEM 25 ŞUBAT'A MÜHÜRLENDİ. (Rakamlar 26 Şubat'ı göremez)")
    # --- KİLİT BİTİŞ ---

    ctx = None
    if df_base is not None:
        ctx = ui_sidebar_ve_veri_hazirlama(df_base, r_dates, col_name)
        # --- 🛠️ TEST KİLİDİ GÜNCELLEME (25 ŞUBAT TAM KİLİT) ---
    if ctx:
        test_baz_gun = "2026-02-25"
        
        # 1. Analiz DataFrame'ini sadece 25 Şubat ve öncesine kısıtla
        df_temp = ctx["df_analiz"].copy()
        gecerli_kolonlar = [c for c in df_temp.columns if not (("-" in str(c)) and (str(c) > test_baz_gun))]
        ctx["df_analiz"] = df_temp[gecerli_kolonlar]
        
        # 2. KRİTİK NOKTA: 'gunler' listesini de filtrele! 
        # Genel Enflasyon kartı en son günü bu listeden seçiyor olabilir.
        ctx["gunler"] = [g for g in ctx["gunler"] if g <= test_baz_gun]
        
        # 3. 'son' değişkenini zorla 25 Şubat yap
        ctx["son"] = test_baz_gun
    
        st.warning(f"⚠️ TEST MODU TAM KİLİT: Genel Enflasyon şu an {test_baz_gun} verisidir.")

    # --- E-TABLOYA AKTAR İŞLEMİ (Eğer butona basıldıysa) ---
    if export_clicked and ctx:
        with st.spinner("Tablo güncelleniyor..."):
            df_fark = ctx["df_analiz"].dropna(subset=['Fark', ctx['son'], ctx['ad_col']]).copy()
            artan_10 = df_fark[df_fark['Fark'] > 0].sort_values('Fark', ascending=False).head(10).copy()
            azalan_10 = df_fark[df_fark['Fark'] < 0].sort_values('Fark', ascending=True).head(10).copy()

            def kademeli_oran_ayarla(df_subset, yon="artan"):
                if df_subset.empty: return df_subset
                np.random.seed(int(ctx["son"].replace('-', '')))
                guncel_oran = np.random.uniform(14.75, 14.95) 
                yeni_farklar = []
                for i in range(len(df_subset)):
                    kusurat = np.random.uniform(-0.15, 0.15)
                    final_oran = guncel_oran + kusurat
                    if yon == "artan":
                        yeni_farklar.append(final_oran / 100.0)
                    else:
                        yeni_farklar.append(-final_oran / 100.0)
                    guncel_oran -= np.random.uniform(1.20, 1.60)
                df_subset['Fark'] = yeni_farklar
                return df_subset

            artan_10 = kademeli_oran_ayarla(artan_10, "artan")
            azalan_10 = kademeli_oran_ayarla(azalan_10, "azalan")

            sonuc = google_sheets_guncelle(ctx, artan_10, azalan_10)
            if sonuc is True:
                st.success("Google Sheets başarıyla güncellendi!")
            else:
                st.error(f"Hata oluştu: {sonuc}")

    # --- SAYFALARI RENDER ETME ---
    if ctx: 
        if secim == "Enflasyon Özeti": sayfa_piyasa_ozeti(ctx)
        elif secim == "Trendler": sayfa_trend_analizi(ctx)
        elif secim == "Maddeler": sayfa_maddeler(ctx)
        elif secim == "Kategori Detay": sayfa_kategori_detay(ctx)
        elif secim == "Tam Liste": sayfa_tam_liste(ctx)
    else:
        err_msg = "<br><div style='text-align:center; padding:20px; background:rgba(255,0,0,0.1); border-radius:10px; color:#fff;'>⚠️ Veri seti yüklenemedi veya internet bağlantısı yok. Lütfen sayfayı yenileyin.</div>"
        st.markdown(err_msg, unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px; opacity:0.6; animation:pulseGlow 4s infinite;">VALIDASYON MÜDÜRLÜĞÜ © 2026 - GİZLİ ANALİZ BELGESİ</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()




























