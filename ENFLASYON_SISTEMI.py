# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib requests

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

        /* --- HEADER VE TOOLBAR GİZLEME --- */
        header {visibility: hidden;}
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        [data-testid="stToolbar"] { display: none; }
        .main .block-container { padding-top: 1rem; }

        /* --- GLOBAL YAZI RENGİ (BEYAZ) --- */
        .stApp, p, h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stDataFrame div, .stDataFrame span {
            color: #ffffff;
        }

        /* --- DROPDOWN (SELECT-BOX) DÜZELTMESİ --- */
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

        /* --- RENKLENDİRME İÇİN ÖZEL SINIFLAR --- */
        .pg-red { color: #fca5a5 !important; }
        .pg-green { color: #6ee7b7 !important; }
        .pg-yellow { color: #fde047 !important; }

        /* --- ANİMASYON TANIMLARI --- */
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

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #090a0c;
            border-right: 1px solid var(--border);
        }

        /* --- YATAY MENÜ --- */
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

        /* --- KART TASARIMLARI --- */
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
        
        /* --- TICKER --- */
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
            animation: marquee 45s linear infinite; /* Hız ayarlandı */
        }
        
        .ticker-item {
            display: inline-block;
            padding: 0 2rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
        }

        /* --- ÜRÜN KARTLARI --- */
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
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# --- 3. RAPOR MOTORU ---
def create_word_report(text_content, tarih, df_analiz=None):
    buffer = BytesIO()
    try:
        doc = Document()
        # Font Ayarları
        style = doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)

        # Başlıklar
        head = doc.add_heading(f'ENFLASYON GÖRÜNÜM RAPORU', 0)
        head.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        subhead = doc.add_paragraph(f'Rapor Tarihi: {tarih}')
        subhead.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        doc.add_paragraph("-" * 50)

        # Metin İçeriği
        paragraphs = text_content.split('\n')
        for p_text in paragraphs:
            if not p_text.strip(): 
                continue
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Bold İşleme (** ile yapılanları bold yap)
            parts = p_text.split('**')
            for i, part in enumerate(parts):
                run = p.add_run(part)
                if i % 2 == 1: 
                    run.bold = True
                    run.font.color.rgb = RGBColor(0, 50, 100)
        
        # Grafik Ekleme (Hata verirse atla ama dosyayı bozma)
        if df_analiz is not None and not df_analiz.empty and 'Fark' in df_analiz.columns:
            try:
                doc.add_page_break()
                doc.add_heading('EKLER: GÖRSEL ANALİZLER', 1)
                
                # Matplotlib Grafiği
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

        # Dosyayı Kaydet
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    except Exception as e:
        # Hata durumunda içinde hata mesajı olan bir dosya döndür
        err_doc = Document()
        err_doc.add_heading('HATA', 0)
        err_doc.add_paragraph(f"Rapor oluşturulurken hata oluştu: {str(e)}")
        buffer = BytesIO()
        err_doc.save(buffer)
        buffer.seek(0)
        return buffer

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
    t = t.replace('.', '').replace(',', '.') if ',' in t and '.' in t else t.replace(',', '.')
    try:
        return float(re.sub(r'[^\d.]', '', t))
    except:
        return None

def kod_standartlastir(k): return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, url):
    fiyat = 0; kaynak = ""; domain = url.lower() if url else ""
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
Tahmin modelimiz, ay sonu kapanışının **%{tahmin:.2f}** bandında olacağını öngörmektedir.

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

# 2. HESAPLAMA YAP
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

# 3. SIDEBAR UI (CONTEXT_HAZIRLA YERİNE)
def ui_sidebar_ve_veri_hazirlama(df_analiz_base, raw_dates, ad_col):
    if df_analiz_base is None: return None
    st.sidebar.markdown("### ⚙️ Veri Ayarları")
    
    # Lottie
    lottie_url = "https://lottie.host/98606416-297c-4a37-9b2a-714013063529/5D6o8k8fW0.json"
    try:
        lottie_json = load_lottieurl(lottie_url)
        with st.sidebar:
             if lottie_json: st_lottie(lottie_json, height=120, key="nav_anim")
    except: pass

    BASLANGIC_LIMITI = "2026-02-04"
    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    if not tum_tarihler:
        st.sidebar.warning("Veri henüz oluşmadı.")
        return None
    secilen_tarih = st.sidebar.selectbox("Rapor Tarihi:", options=tum_tarihler, index=0)
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌍 Piyasalar")
    symbols = [ {"s": "FX_IDC:USDTRY", "d": "Dolar / TL"}, {"s": "FX_IDC:EURTRY", "d": "Euro / TL"}, {"s": "FX_IDC:XAUTRYG", "d": "Gram Altın"}, {"s": "TVC:UKOIL", "d": "Brent Petrol"}, {"s": "BINANCE:BTCUSDT", "d": "Bitcoin ($)"} ]
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
# ANA SAYFA FONKSİYONU KALDIRILDI

def sayfa_piyasa_ozeti(ctx):
    # --- 1. KPI KARTLARI ---
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="kpi-card"><div class="kpi-title">GENEL ENFLASYON</div><div class="kpi-value">%{ctx["enf_genel"]:.2f}</div><div class="kpi-sub" style="color:#ef4444; font-size:12px;">Aylık Değişim</div></div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="kpi-card"><div class="kpi-title">GIDA ENFLASYONU</div><div class="kpi-value">%{ctx["enf_gida"]:.2f}</div><div class="kpi-sub" style="color:#fca5a5; font-size:12px;">Mutfak Sepeti</div></div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="kpi-card"><div class="kpi-title">AY SONU BEKLENTİ</div><div class="kpi-value">%{ctx["tahmin"]:.2f}</div><div class="kpi-sub" style="color:#a78bfa; font-size:12px;">AI Projeksiyonu</div></div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="kpi-card"><div class="kpi-title">RESMİ (TÜİK) VERİSİ</div><div class="kpi-value">%{ctx["resmi_aylik_degisim"]:.2f}</div><div class="kpi-sub" style="color:#fbbf24; font-size:12px;">Son Açıklanan Aylık</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- 2. TICKER (KAYAN YAZI) ---
    df = ctx["df_analiz"]
    
    # En çok artan (Enflasyonist - Kötü - Kırmızı)
    inc = df.sort_values('Gunluk_Degisim', ascending=False).head(10)
    # En çok düşen (Deflasyonist - İyi - Yeşil)
    dec = df.sort_values('Gunluk_Degisim', ascending=True).head(10)
    
    items = []
    
    # ARTANLAR İÇİN DÖNGÜ (KIRMIZI RENK)
    for _, r in inc.iterrows():
        val = r['Gunluk_Degisim']
        if val > 0:
            # Inline CSS ile kırmızı renk zorlanıyor ve font kalınlaştırılıyor
            items.append(f"<span style='color:#ef4444; font-weight:800;'>▲ {r[ctx['ad_col']]} %{val*100:.1f}</span>")
            
    # DÜŞENLER İÇİN DÖNGÜ (YEŞİL RENK)
    for _, r in dec.iterrows():
        val = r['Gunluk_Degisim']
        if val < 0:
            # Inline CSS ile yeşil renk zorlanıyor ve font kalınlaştırılıyor
            items.append(f"<span style='color:#22c55e; font-weight:800;'>▼ {r[ctx['ad_col']]} %{abs(val)*100:.1f}</span>")
            
    # Listeyi birleştir
    ticker_str = " &nbsp;&nbsp;&nbsp; • &nbsp;&nbsp;&nbsp; ".join(items)
    if not ticker_str: ticker_str = "Veri bekleniyor..."

    # --- 3. TICKER HTML BLOĞU ---
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
    
    # --- 4. GRAFİK VE LİSTE ---
    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        fig_hist = px.histogram(df, x="Fark_Yuzde", nbins=20, title="Fiyat Değişim Dağılımı", color_discrete_sequence=["#3b82f6"])
        fig_hist.update_layout(bargap=0.1)
        fig_hist.update_xaxes(title_text=None, showticklabels=False, ticks="", showgrid=False, visible=False)
        st.plotly_chart(style_chart(fig_hist), use_container_width=True)
        
    with col_g2:
        # Sağ taraftaki özet kutusu
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
    
    # --- 5. TREE MAP ---
    st.subheader("Sektörel Isı Haritası")
    fig_tree = px.treemap(df, path=[px.Constant("Enflasyon Sepeti"), 'Grup', ctx['ad_col']], values=ctx['agirlik_col'], color='Fark', color_continuous_scale='RdYlGn_r')
    st.plotly_chart(style_chart(fig_tree, is_sunburst=True), use_container_width=True)

def sayfa_kategori_detay(ctx):
    df = ctx["df_analiz"]
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
    
    # Rapor metnini oluştur
    rap_text = generate_detailed_static_report(
        ctx["df_analiz"], ctx["son"], ctx["enf_genel"], 
        ctx["enf_gida"], ctx["gun_farki"], ctx["tahmin"], 
        ctx["ad_col"], ctx["agirlik_col"]
    )
    
    # Ekrana bas (HTML olarak)
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.03); padding:30px; border-radius:12px; border:1px solid rgba(255,255,255,0.1); font-family:'Inter'; line-height:1.8; animation:fadeInUp 0.5s;">
        {rap_text.replace(chr(10), '<br>').replace('**', '<b>').replace('**', '</b>')}
    </div>
    """, unsafe_allow_html=True)
    
    # Word dosyasını hazırla
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
    st.markdown("### 📦 Madde Bazlı Değişim Analizi")
    st.markdown("<p style='color:#a1a1aa; font-size:14px;'>Seçilen kategorideki ürünlerin, baz alınan tarihe göre oransal değişimlerini gösterir.</p>", unsafe_allow_html=True)
    kategoriler = sorted(df['Grup'].unique().tolist())
    col1, col2 = st.columns([1, 3])
    with col1: secilen_kat = st.selectbox("Kategori Seçiniz:", options=kategoriler, index=0)
    df_sub = df[df['Grup'] == secilen_kat].copy().sort_values('Fark_Yuzde', ascending=True)
    if not df_sub.empty:
        colors = []
        for x in df_sub['Fark_Yuzde']:
            if abs(x) < 0.01: colors.append('#fde047')
            elif x > 0: colors.append('#ef4444')
            else: colors.append('#10b981')
        
        fig = go.Figure(go.Bar(x=df_sub['Fark_Yuzde'], y=df_sub[ctx['ad_col']], orientation='h', marker_color=colors, text=df_sub['Fark_Yuzde'].apply(lambda x: f"%{x:.2f}"), textposition='outside', hovertemplate='<b>%{y}</b><br>Değişim: %%{x:.2f}<extra></extra>'))
        fig.update_layout(height=max(500, len(df_sub) * 30), title=f"{secilen_kat} Grubu Fiyat Değişimleri", xaxis_title="Değişim Oranı (%)", yaxis=dict(title="", showgrid=False), margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(style_chart(fig), use_container_width=True)
    else: st.warning("Bu kategoride veri bulunamadı.")

def sayfa_trend_analizi(ctx):
    st.markdown("### 📈 Zaman Serisi ve Enflasyon Trendleri")
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
        fig_genel = px.line(df_endeks, x='Tarih', y='Kümülatif_Degisim', title="GENEL ENFLASYON TRENDİ", markers=True)
        fig_genel.update_traces(line_color='#3b82f6', line_width=4, marker_size=8)
        st.plotly_chart(style_chart(fig_genel), use_container_width=True)
        st.info(f"ℹ️ Grafik, {gunler[0]} tarihini baz alarak hesaplanan kümülatif sepet değişimini gösterir.")
    
    st.markdown("---")
    st.subheader("Ürün Bazlı Fiyat Trendleri")
    seçilen_urunler = st.multiselect("Grafiğe eklenecek ürünleri seçin:", options=df[ctx['ad_col']].unique(), default=df.sort_values('Fark_Yuzde', ascending=False).head(3)[ctx['ad_col']].tolist())
    if seçilen_urunler:
        df_melted = df[df[ctx['ad_col']].isin(seçilen_urunler)][[ctx['ad_col']] + gunler].melt(id_vars=[ctx['ad_col']], var_name='Tarih', value_name='Fiyat')
        base_prices = df_melted[df_melted['Tarih'] == gunler[0]].set_index(ctx['ad_col'])['Fiyat'].to_dict()
        df_melted['Yuzde_Degisim'] = df_melted.apply(lambda row: ((row['Fiyat']/base_prices.get(row[ctx['ad_col']], 1)) - 1)*100 if base_prices.get(row[ctx['ad_col']], 0) > 0 else 0, axis=1)
        st.plotly_chart(style_chart(px.line(df_melted, x='Tarih', y='Yuzde_Degisim', color=ctx['ad_col'], title="Ürün Bazlı Kümülatif Değişim (%)", markers=True)), use_container_width=True)

# --- ANA MAIN ---
def main():
    
    # --- AYAR: SENKRONİZASYON BUTONU ---
    # Bu ayarı False yaparak butonu tamamen gizleyebilirsiniz.
    SENKRONIZASYON_AKTIF = True 

    # --- Üst Bilgi Barı (Sticky Header) ---
    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; padding:15px 25px; 
            background:linear-gradient(90deg, #0f172a 0%, #1e1b4b 100%); border-radius:12px; margin-bottom:20px; margin-top:-30px; animation: fadeInUp 0.5s;">
            <div>
                <div style="font-weight:800; font-size:24px; color:#fff;">
                    Enflasyon Monitörü 
                    <span style="background:rgba(16,185,129,0.15); color:#34d399; font-size:10px; padding:3px 8px; border-radius:4px; border:1px solid rgba(16,185,129,0.2); vertical-align: middle;">SİMÜLASYON</span>
                </div>
                <div style="font-size:12px; color:#94a3b8;">Yapay Zeka Destekli Enflasyon Analiz Platformu</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:10px; color:#64748b; font-weight:700; letter-spacing:1.5px;">İSTANBUL</div>
                <div style="font-size:20px; font-weight:700; color:#e2e8f0; font-family:'JetBrains Mono';">{datetime.now().strftime("%d.%m.%Y")}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Menü Tanımları (Ana Sayfa Kaldırıldı) ---
    menu_items = {
        "📊 Enflasyon Özeti": "Enflasyon Özeti", 
        "📈 Trendler": "Trendler",
        "📦 Maddeler": "Maddeler",
        "🏷️ Kategori Detay": "Kategori Detay",
        "📋 Tam Liste": "Tam Liste",
        "📝 Raporlama": "Raporlama"
    }
    
    # Menü Radyo Butonu
    secilen_etiket = st.radio(
        "Navigasyon", 
        options=list(menu_items.keys()), 
        label_visibility="collapsed", 
        key="nav_radio",
        horizontal=True
    )
    secim = menu_items[secilen_etiket]

    # --- Senkronizasyon Butonu (İsteğe Bağlı) ---
    if SENKRONIZASYON_AKTIF:
        col_empty, col_btn = st.columns([4, 1])
        with col_btn:
            if st.button("SİSTEMİ SENKRONİZE ET ⚡", type="primary", use_container_width=True):
                progress_bar = st.progress(0, text="Veri akışı sağlanıyor...")
                res = html_isleyici(lambda p: progress_bar.progress(min(1.0, max(0.0, p)), text="Senkronizasyon sürüyor..."))
                progress_bar.progress(1.0, text="Tamamlandı!"); time.sleep(0.5); progress_bar.empty()
                
                if "OK" in res:
                    st.cache_data.clear()
                    st.toast('Sistem Senkronize Edildi!', icon='🚀')
                    time.sleep(1)
                    st.rerun()
                elif "Veri bulunamadı" in res: 
                    st.warning("⚠️ Yeni veri akışı yok.")
                else: 
                    st.error(res)

    # --- Veri Yükleme ---
    with st.spinner("Veri tabanına bağlanılıyor..."):
        df_base, r_dates, col_name = verileri_getir_cache()
    
    ctx = None
    if df_base is not None:
        ctx = ui_sidebar_ve_veri_hazirlama(df_base, r_dates, col_name)

    # --- Sayfa Yönlendirme (ROUTER) ---
    if ctx: 
        if secim == "Enflasyon Özeti": sayfa_piyasa_ozeti(ctx)
        elif secim == "Trendler": sayfa_trend_analizi(ctx)
        elif secim == "Maddeler": sayfa_maddeler(ctx)
        elif secim == "Kategori Detay": sayfa_kategori_detay(ctx)
        elif secim == "Tam Liste": sayfa_tam_liste(ctx)
        elif secim == "Raporlama": sayfa_raporlama(ctx)
    else:
        # Veri yüklenemediyse uyarı ver
        err_msg = "<br><div style='text-align:center; padding:20px; background:rgba(255,0,0,0.1); border-radius:10px; color:#fff;'>⚠️ Veri seti yüklenemedi veya internet bağlantısı yok. Lütfen sayfayı yenileyin.</div>"
        st.markdown(err_msg, unsafe_allow_html=True)

    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px; opacity:0.6;">VALIDASYON MUDURLUGU © 2026 - GİZLİ ANALİZ BELGESİ</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
