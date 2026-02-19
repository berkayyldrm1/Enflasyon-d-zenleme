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
    page_title="Enflasyon Monitörü | Pro Analytics",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded"
)

# --- CSS MOTORU ---
def apply_theme():
    if 'plotly_template' not in st.session_state:
        st.session_state.plotly_template = "plotly_dark"

    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

        header {visibility: hidden;}
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        [data-testid="stToolbar"] { display: none; }
        .main .block-container { padding-top: 1rem; }

        .stApp, p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stDataFrame div, .stDataFrame span {
            color: #ffffff;
        }

        div[data-baseweb="select"] > div {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.05);
        }
        div[data-baseweb="popover"] div, 
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] span {
            color: #000000 !important; 
        }
        div[data-baseweb="menu"] {
            background-color: #f0f2f6 !important;
        }
        div[data-baseweb="menu"] li:hover {
            background-color: #e2e8f0 !important;
        }

        .pg-red { color: #fca5a5 !important; }
        .pg-green { color: #6ee7b7 !important; }
        .pg-yellow { color: #fde047 !important; }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translate3d(0, 20px, 0); }
            to { opacity: 1; transform: translate3d(0, 0, 0); }
        }
        
        @keyframes marquee {
            0% { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        :root {
            --bg-dark: #0f1116;
            --card-bg: rgba(30, 33, 40, 0.7);
            --border: rgba(255, 255, 255, 0.08);
            --accent: #3b82f6;
        }

        .stApp {
            background-color: var(--bg-dark);
            font-family: 'Inter', sans-serif;
        }

        section[data-testid="stSidebar"] {
            background-color: #090a0c;
            border-right: 1px solid var(--border);
        }

        [data-testid="stRadio"] > label {
            display: none !important;
        }
        
        [data-testid="stRadio"] > div {
            display: flex;
            flex-direction: row;
            flex-wrap: nowrap !important;
            overflow-x: auto;
            justify-content: center;
            align-items: center;
            gap: 8px;
            background: rgba(30, 33, 40, 0.4);
            padding: 8px;
            border-radius: 16px;
            border: 1px solid var(--border);
            margin-top: -20px;
            white-space: nowrap;
        }
        
        [data-testid="stRadio"] > div::-webkit-scrollbar { height: 4px; }
        [data-testid="stRadio"] > div::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }

        [data-testid="stRadio"] label {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 8px 12px;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            font-family: 'Inter', sans-serif;
            font-weight: 500;
            font-size: 13px;
            color: #ffffff !important;
            min-width: auto;
            flex: 0 0 auto;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        [data-testid="stRadio"] label p { color: #ffffff !important; margin: 0; }

        [data-testid="stRadio"] label:hover {
            background-color: rgba(59, 130, 246, 0.2);
            border-color: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
        }

        [data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            border-color: #60a5fa;
            font-weight: 700;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        }

        .kpi-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            animation: fadeInUp 0.6s ease-out both;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .kpi-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.3);
            border-color: rgba(59, 130, 246, 0.4);
        }

        .kpi-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            color: #94a3b8 !important;
            font-weight: 600;
            margin-bottom: 8px;
        }

        .kpi-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 32px;
            font-weight: 700;
            color: #ffffff !important;
            text-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
        }
        
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background: rgba(255,255,255,0.02);
            border-top: 1px solid var(--border);
            border-bottom: 1px solid var(--border);
            padding: 10px 0;
            margin-bottom: 20px;
            white-space: nowrap;
            position: relative;
        }
        
        .ticker-move {
            display: inline-block;
            white-space: nowrap;
            animation: marquee 45s linear infinite;
        }
        
        .ticker-item {
            display: inline-block;
            padding: 0 2rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        }

        .pg-card {
            background: linear-gradient(145deg, rgba(30, 33, 40, 0.6), rgba(20, 23, 30, 0.8));
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 15px;
            animation: fadeInUp 0.5s ease-out both;
            transition: all 0.3s;
            height: 100%;
        }
        
        .pg-card:hover {
            transform: scale(1.03);
            border-color: var(--accent);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.2);
        }
        
        .pg-name { font-size: 13px; font-weight: 500; color: #ffffff !important; margin-bottom: 8px; height: 32px; overflow: hidden; }
        .pg-price { font-family: 'JetBrains Mono'; font-size: 18px; font-weight: 700; color: #ffffff !important; }
        
        .pg-badge { 
            font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 6px; 
            margin-top: 8px; display: inline-block;
        }
        .pg-red { background: rgba(239, 68, 68, 0.2); color: #fca5a5 !important; border: 1px solid rgba(239, 68, 68, 0.3); }
        .pg-green { background: rgba(16, 185, 129, 0.2); color: #6ee7b7 !important; border: 1px solid rgba(16, 185, 129, 0.3); }
        .pg-yellow { background: rgba(234, 179, 8, 0.2); color: #fde047 !important; border: 1px solid rgba(234, 179, 8, 0.3); }

        div.stButton > button {
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white !important;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s;
        }
        div.stButton > button:hover {
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
            transform: translateY(-2px);
        }
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

# --- 3. RAPOR MOTORU ---
def create_word_report(text_content, tarih, df_analiz=None):
    buffer = BytesIO()
    try:
        doc = Document()
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)

        head = doc.add_heading(f'ENFLASYON GÖRÜNÜM RAPORU', 0)
        head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        subhead = doc.add_paragraph(f'Rapor Tarihi: {tarih}')
        subhead.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph("-" * 50)

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
        
        if df_analiz is not None and not df_analiz.empty and 'Fark' in df_analiz.columns:
            try:
                doc.add_page_break()
                doc.add_heading('EKLER: GÖRSEL ANALİZLER', 1)
                
                data = pd.to_numeric(df_analiz['Fark'], errors='coerce').dropna() * 100
                if not data.empty:
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.hist(data, bins=20, color='#3b82f6', edgecolor='black', alpha=0.7)
                    ax.set_title(f"Fiyat Değişim Dağılımı (%)", fontsize=12)
                    ax.set_xlabel("Değişim Oranı (%)")
                    ax.set_ylabel("Ürün Sayısı")
                    
                    img_buffer = BytesIO()
                    plt.savefig(img_buffer, format='png', dpi=100)
                    plt.close(fig)
                    img_buffer.seek(0)
                    
                    doc.add_picture(img_buffer, width=Inches(5.5))
                    doc.add_paragraph("Grafik 1: Ürünlerin fiyat değişim oranlarına göre dağılımı.", style='Caption')
            except Exception as img_err:
                doc.add_paragraph(f"[Grafik oluşturulamadı: {str(img_err)}]")

        doc.save(buffer)
        buffer.seek(0)
        return buffer

    except Exception as e:
        err_doc = Document()
        err_doc.add_heading('HATA', 0)
        err_doc.add_paragraph(f"Rapor oluşturulurken hata oluştu: {str(e)}")
        buffer = BytesIO()
        err_doc.save(buffer)
        buffer.seek(0)
        return buffer

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

# --- 5. RESMİ ENFLASYON ---
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
**ENFLASYON GÖRÜNÜM RAPORU**
**Tarih:** {tarih}

**1. 📊 ANA GÖSTERGELER**
-----------------------------------------
**GENEL ENFLASYON** : **%{enf_genel:.2f}**
**GIDA ENFLASYONU** : **%{enf_gida:.2f}**
**AY SONU TAHMİNİ** : **%{tahmin:.2f}**
-----------------------------------------

**2. 🔎 ENFLASYON RÖNTGENİ**
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
Hesaplanan verilere göre ay sonu projeksiyonu **%{tahmin:.2f}** bandında seyretmektedir.

---
*Otomatik Rapor Sistemi | Validasyon Müdürlüğü*
"""
    return text.strip()

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

def verileri_getir_cache():
    try:
        repo = get_github_repo()
        if not repo: 
            st.sidebar.error("Repo bağlantısı kurulamadı.")
            return None, None, None
            
        branch_name = st.secrets["github"]["branch"]
        
        # 1. GITHUB ÇEKİRDEĞİNE İNİYORUZ (Önbelleksiz kesin çözüm)
        latest_commit = repo.get_branch(branch_name).commit
        tree = repo.get_git_tree(latest_commit.sha, recursive=True)
        
        fiyat_blob_sha = None
        conf_blob_sha = None
        
        for item in tree.tree:
            if item.path == FIYAT_DOSYASI: fiyat_blob_sha = item.sha
            elif item.path == EXCEL_DOSYASI: conf_blob_sha = item.sha
                
        if not fiyat_blob_sha:
            st.sidebar.error(f"{FIYAT_DOSYASI} repoda bulunamadı!")
            return None, None, None
            
        # 2. DOSYAYI DOĞRUDAN BLOB OLARAK İNDİR (Sıfır Cache)
        fiyat_blob = repo.get_git_blob(fiyat_blob_sha)
        fiyat_content = base64.b64decode(fiyat_blob.content)
        df_f = pd.read_excel(BytesIO(fiyat_content), dtype=str)

        if conf_blob_sha:
            conf_blob = repo.get_git_blob(conf_blob_sha)
            conf_content = base64.b64decode(conf_blob.content)
            df_s = pd.read_excel(BytesIO(conf_content), sheet_name=SAYFA_ADI, dtype=str)
        else: df_s = pd.DataFrame()

        if df_f.empty or df_s.empty: return None, None, None

        # --- AGRESİF TARİH KURTARMA OPERASYONU ---
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
        
        # Radarı tasarıma zarar vermeyecek şekilde ufak bir expander içine gizledik
        with st.sidebar.expander("🛠️ Sistem Radarı", expanded=False):
            st.caption("Veritabanına İşlenen Son Günler:")
            st.write(raw_dates[-3:] if len(raw_dates)>2 else raw_dates)

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
        if pivot.empty: return None, None, None

        if 'Grup' not in df_s.columns:
            grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut"}
            df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")

        df_analiz_base = pd.merge(df_s, pivot, on='Kod', how='left')
        return df_analiz_base, raw_dates, ad_col

    except Exception as e:
        st.sidebar.error(f"Veri Çekme Hatası: {str(e)}")
        return None, None, None

# 2. HESAPLAMA YAP (SİMÜLASYON AKTİF EDİLDİ)
def hesapla_metrikler(df_analiz_base, secilen_tarih, gunler, tum_gunler_sirali, ad_col, agirlik_col, baz_col, aktif_agirlik_col, son):
    df_analiz = df_analiz_base.copy()
    
    # --- AYAR 1: AYLIK ENFLASYON SİMÜLASYONU ---
    SIM_ALT_LIMIT = 1.025  # %2.0
    SIM_UST_LIMIT = 1.042  # %4.5
    
    # --- AYAR 2: YILLIK ENFLASYON HEDEFİ ---
    BEKLENEN_AYLIK_ORT = 2.25 
    
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
        
        # 1. ADIM: GERÇEK ORANI HESAPLA
        base_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
        
        # 2. ADIM: SİMÜLASYON ŞOKU EKLE
        simulasyon_soku = np.random.uniform(SIM_ALT_LIMIT, SIM_UST_LIMIT, size=len(base_rel))
        p_rel = base_rel * simulasyon_soku
        
        # Simüle edilmiş yeni fiyatlar
        gecerli_veri['Simule_Fiyat'] = gecerli_veri[baz_col] * p_rel
        
        # Ana tabloyu güncelle 
        df_analiz.loc[gecerli_veri.index, 'Aylik_Ortalama'] = gecerli_veri['Simule_Fiyat']

        # 3. ADIM: GENEL ENFLASYON HESABI
        if w.sum() > 0: 
            enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
        
        # 4. ADIM: GIDA ENFLASYONU HESABI
        gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
        if not gida_df.empty and gida_df[aktif_agirlik_col].sum() > 0:
            gida_rel = gida_df['Simule_Fiyat'] / gida_df[baz_col]
            enf_gida = ((gida_df[aktif_agirlik_col] * gida_rel).sum() / gida_df[aktif_agirlik_col].sum() * 100) - 100

        # 5. ADIM: YILLIK ENFLASYON (HEDEF %30-35 BANDI)
        if enf_genel > 0:
            yillik_enf = ((1 + enf_genel/100) * (1 + BEKLENEN_AYLIK_ORT/100)**11 - 1) * 100
            yillik_enf = yillik_enf * np.random.uniform(0.98, 1.02)
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

    resmi_aylik_degisim = 0.0
    try:
        df_resmi, _ = get_official_inflation()
        if df_resmi is not None and not df_resmi.empty:
             resmi_aylik_degisim = ((df_resmi.iloc[-1]['Resmi_TUFE'] / df_resmi.iloc[-2]['Resmi_TUFE']) - 1) * 100
    except: pass

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
        <div style="background:rgba(255,255,255,0.05); padding:12px; border-radius:8px; border-left: 3px solid {renk}; margin-bottom:10px;">
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
        widget_code = f"""<div class="tradingview-widget-container" style="border-radius:8px; overflow:hidden; margin-bottom:8px;"><div class="tradingview-widget-container__widget"></div><script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>{{ "symbol": "{sym['s']}", "width": "100%", "height": 100, "locale": "tr", "dateRange": "1D", "colorTheme": "dark", "isTransparent": true, "autosize": true, "largeChartUrl": "" }}</script></div>"""
        with st.sidebar: components.html(widget_code, height=100)
    
    return ctx

# --- SAYFA FONKSİYONLARI ---

def sayfa_piyasa_ozeti(ctx):
    c1, c2, c3, c4 = st.columns(4)
    
    with c1: 
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">GENEL ENFLASYON</div><div class="kpi-value">%{ctx["enf_genel"]:.2f}</div><div class="kpi-sub" style="color:#ef4444; font-size:12px;">Aylık Değişim (Simüle)</div></div>', unsafe_allow_html=True)
    with c2: 
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">GIDA ENFLASYONU</div><div class="kpi-value">%{ctx["enf_gida"]:.2f}</div><div class="kpi-sub" style="color:#fca5a5; font-size:12px;">Mutfak Sepeti</div></div>', unsafe_allow_html=True)
    with c3: 
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">YILLIK ENFLASYON</div><div class="kpi-value">%{ctx["yillik_enf"]:.2f}</div><div class="kpi-sub" style="color:#a78bfa; font-size:12px;">Yıllık Projeksiyon</div></div>', unsafe_allow_html=True)
    with c4: 
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">RESMİ (TÜİK) VERİSİ</div><div class="kpi-value">%{ctx["resmi_aylik_degisim"]:.2f}</div><div class="kpi-sub" style="color:#fbbf24; font-size:12px;">Son Açıklanan Aylık</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    df = ctx["df_analiz"]
    inc = df.sort_values('Gunluk_Degisim', ascending=False).head(5)
    dec = df.sort_values('Gunluk_Degisim', ascending=True).head(5)
    
    items = []
    for _, r in inc.iterrows():
        val = r['Gunluk_Degisim']
        if val > 0:
            items.append(f"<span style='color:#ef4444; font-weight:800;'>▲ {r[ctx['ad_col']]} %{val*100:.1f}</span>")
            
    for _, r in dec.iterrows():
        val = r['Gunluk_Degisim']
        if val < 0:
            items.append(f"<span style='color:#22c55e; font-weight:800;'>▼ {r[ctx['ad_col']]} %{abs(val)*100:.1f}</span>")
            
    ticker_str = " &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp; ".join(items)
    if not ticker_str: ticker_str = "Veri bekleniyor..."

    ticker_html = f"""
    <div class="ticker-wrap" style="background: rgba(255,255,255,0.02); border-top:1px solid rgba(255,255,255,0.1); border-bottom:1px solid rgba(255,255,255,0.1); padding:10px 0; margin-bottom:20px;">
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
       if not df_trend.empty: df_trend = df_trend.sort_values('Tarih')

       if not df_trend.empty:
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
       <div class="kpi-card" style="height:100%">
           <div style="font-size:12px; color:#94a3b8; font-weight:700;">YÜKSELENLER</div>
           <div style="font-size:24px; color:#ef4444; font-weight:700;">{len(df[df['Fark'] > 0])} Ürün</div>
           <div style="margin: 20px 0; border-top:1px solid rgba(255,255,255,0.1)"></div>
           <div style="font-size:12px; color:#94a3b8; font-weight:700;">DÜŞENLER</div>
           <div style="font-size:24px; color:#22c55e; font-weight:700;">{len(df[df['Fark'] < 0])} Ürün</div>
       </div>
       """
       st.markdown(ozet_html, unsafe_allow_html=True)

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
        page_num = st.number_input("Sayfa", min_value=1, max_value=max(1, len(df_show)//items_per_page + 1), step=1)
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

def sayfa_raporlama(ctx):
    st.markdown("### 📝 Stratejik Enflasyon Raporu")
    
    rap_text = generate_detailed_static_report(
        ctx["df_analiz"], ctx["son"], ctx["enf_genel"], 
        ctx["enf_gida"], ctx["gun_farki"], ctx["tahmin"], 
        ctx["ad_col"], ctx["agirlik_col"]
    )
    
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); padding:30px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); font-family:'Inter'; line-height:1.8; animation:fadeInUp 0.5s;">
        {rap_text.replace(chr(10), '<br>').replace('**', '<b>').replace('**', '</b>')}
    </div>
    """, unsafe_allow_html=True)
    
    word_buffer = create_word_report(rap_text, ctx["son"], ctx["df_analiz"])
    
    st.download_button(
        label="📥 Word Raporu İndir",
        data=word_buffer,
        file_name=f"Enflasyon_Raporu_{ctx['son']}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        key="download_word_btn"
    )

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

    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:15px 25px; 
            background:linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%); border-radius:12px; margin-bottom:20px; margin-top:-30px; animation: fadeInUp 0.5s;">
            <div>
                <div style="font-weight:800; font-size:24px; color:#fff;">
                    Enflasyon Monitörü 
                    <span style="background:rgba(59,130,246,0.15); color:#60a5fa; font-size:10px; padding:3px 8px; border-radius:4px; border:1px solid rgba(59,130,246,0.2); vertical-align: middle;">SİMÜLASYON AKTİF</span>
                </div>
                <div style="font-size:12px; color:#94a3b8;">Yapay Zeka Destekli Enflasyon Analiz Platformu</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; color:#64748b; font-weight:700; letter-spacing:1.5px;">TÜRKİYE SAATİ</div>
                <div style="font-size:20px; font-weight:700; color:#e2e8f0; font-family:'JetBrains Mono';">{(datetime.utcnow() + timedelta(hours=3)).strftime("%d.%m.%Y")}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    menu_items = {
        "📊 Enflasyon Özeti": "Enflasyon Özeti", 
        "📈 Trendler": "Trendler",
        "📦 Maddeler": "Maddeler",
        "🏷️ Kategori Detay": "Kategori Detay",
        "📋 Tam Liste": "Tam Liste",
        "📝 Raporlama": "Raporlama"
    }
    
    secilen_etiket = st.radio(
        "Navigasyon", 
        options=list(menu_items.keys()), 
        label_visibility="collapsed", 
        key="nav_radio",
        horizontal=True
    )
    secim = menu_items[secilen_etiket]

    if SENKRONIZASYON_AKTIF:
        col_empty, col_btn = st.columns([4, 1])
        with col_btn:
            sync_clicked = st.button("SİSTEMİ SENKRONİZE ET ⚡", type="primary", use_container_width=True)

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
        df_base, r_dates, col_name = verileri_getir_cache()
    
    ctx = None
    if df_base is not None:
        ctx = ui_sidebar_ve_veri_hazirlama(df_base, r_dates, col_name)

    if ctx: 
        if secim == "Enflasyon Özeti": sayfa_piyasa_ozeti(ctx)
        elif secim == "Trendler": sayfa_trend_analizi(ctx)
        elif secim == "Maddeler": sayfa_maddeler(ctx)
        elif secim == "Kategori Detay": sayfa_kategori_detay(ctx)
        elif secim == "Tam Liste": sayfa_tam_liste(ctx)
        elif secim == "Raporlama": sayfa_raporlama(ctx)
    else:
        err_msg = "<br><div style='text-align:center; padding:20px; background:rgba(255,0,0,0.1); border-radius:10px; color:#fff;'>⚠️ Veri seti yüklenemedi veya internet bağlantısı yok. Lütfen sayfayı yenileyin.</div>"
        st.markdown(err_msg, unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px; opacity:0.6;">VALIDASYON MUDURLUGU © 2026 - GİZLİ ANALİZ BELGESİ</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()


