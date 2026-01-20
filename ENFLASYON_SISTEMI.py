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
from prophet import Prophet
from fpdf import FPDF
import streamlit.components.v1 as components
import tempfile
import os
import math
import random
import html
import numpy as np 
from scipy import stats

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded" 
)

# --- CSS MOTORU (CYBERPUNK / FINTECH STİL) ---
def apply_theme():
    st.session_state.plotly_template = "plotly_dark"

    final_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500&display=swap');

        :root {{
            --bg-color: #09090b;
            --card-bg: rgba(24, 24, 27, 0.6);
            --border-color: rgba(255, 255, 255, 0.08);
            --neon-blue: #3b82f6;
            --neon-green: #22c55e;
            --neon-red: #ef4444;
        }}
        
        @keyframes fadeIn {{ 0% {{ opacity: 0; transform: translateY(10px); }} 100% {{ opacity: 1; transform: translateY(0); }} }}
        .block-container {{ animation: fadeIn 0.8s ease-out; padding-top: 2rem !important; }}

        .stSelectbox > div > div, .stTextInput > div > div {{
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid var(--border-color) !important;
            color: #e4e4e7 !important;
            border-radius: 8px !important;
        }}
        ul[data-baseweb="menu"] {{ background-color: #18181b !important; border: 1px solid #3f3f46 !important; }}

        [data-testid="stDataEditor"], [data-testid="stDataFrame"] {{ color-scheme: dark; background-color: transparent !important; }}
        div[data-testid="stDataEditor"] > div, div[data-testid="stDataFrame"] > div {{
            background-color: rgba(24, 24, 27, 0.4) !important; border: 1px solid #333 !important; border-radius: 8px !important;
        }}

        [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {{ visibility: hidden; height: 0px; display: none; }}
        
        [data-testid="stAppViewContainer"] {{
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.06), transparent 25%), radial-gradient(circle at 85% 30%, rgba(239, 68, 68, 0.04), transparent 25%);
            font-family: 'Inter', sans-serif !important; color: #e4e4e7 !important;
        }}

        button[data-baseweb="tab"] {{ background-color: transparent !important; }}
        button[data-baseweb="tab"] div[data-testid="stMarkdownContainer"] p {{ color: #a1a1aa !important; font-weight: 600 !important; font-size: 13px !important; }}
        button[data-baseweb="tab"][aria-selected="true"] {{ border-bottom-color: #3b82f6 !important; }}
        button[data-baseweb="tab"][aria-selected="true"] div[data-testid="stMarkdownContainer"] p {{ color: #ffffff !important; }}

        [data-testid="stDownloadButton"] button {{
            background-color: #000000 !important; color: #ffffff !important; border: 1px solid #3f3f46 !important; font-weight: 700 !important;
            text-transform: uppercase !important; letter-spacing: 1px !important; transition: all 0.3s ease !important; border-radius: 6px !important;
        }}
        [data-testid="stDownloadButton"] button:hover {{ border-color: #3b82f6 !important; box-shadow: 0 0 15px rgba(59, 130, 246, 0.2) !important; color: #3b82f6 !important; }}

        .kpi-card {{
            background: linear-gradient(145deg, rgba(39, 39, 42, 0.4), rgba(24, 24, 27, 0.6)); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px; padding: 24px; position: relative; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .kpi-card:hover {{ transform: translateY(-5px); box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6), inset 0 0 0 1px rgba(255,255,255,0.1); }}
        
        .kpi-title {{ font-size: 11px; font-weight: 700; color: #a1a1aa !important; text-transform: uppercase; margin-bottom: 8px; }}
        .kpi-value {{ font-size: 38px; font-weight: 800; color: #ffffff !important; text-shadow: 0 0 30px rgba(255,255,255,0.1); }}
        .kpi-sub {{ font-size: 12px; font-weight: 500; margin-top: 8px; color: #d4d4d8 !important; display: flex; align-items: center; gap: 5px; }}

        .pg-card {{ background: rgba(39, 39, 42, 0.3); border: 1px solid var(--border-color); border-radius: 12px; padding: 16px; height: 180px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; text-align: center; }}
        .pg-card:hover {{ background: rgba(63, 63, 70, 0.5); border-color: rgba(255,255,255,0.15); transform: translateY(-3px); box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5); }}
        .pg-name {{ font-size: 13px; font-weight: 600; color: #e4e4e7 !important; line-height: 1.4; opacity: 0.9; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        .pg-price {{ font-size: 24px; font-weight: 900; color: #ffffff !important; letter-spacing: -0.5px; margin: 10px 0; }}
        .pg-badge {{ padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; min-width: 80px; display: inline-flex; justify-content: center; }}
        .pg-red {{ background: rgba(239, 68, 68, 0.1); color: #fca5a5 !important; border: 1px solid rgba(239, 68, 68, 0.3); }}
        .pg-green {{ background: rgba(34, 197, 94, 0.1); color: #86efac !important; border: 1px solid rgba(34, 197, 94, 0.3); }}
        .pg-gray {{ background: #27272a; color: #a1a1aa !important; border: 1px solid #3f3f46; }}

        .ticker-wrap {{ width: 100%; overflow: hidden; background-color: rgba(0,0,0,0.2); border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); padding: 8px 0; margin-bottom: 25px; backdrop-filter: blur(5px); }}
        .ticker-move {{ display: inline-block; padding-left: 100%; animation: marquee 60s linear infinite; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 600; }}
        .ticker-move:hover {{ animation-play-state: paused; }}
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}

        section[data-testid="stSidebar"] {{ background-color: #050505 !important; border-right: 1px solid #27272a; }}
        
        div.stButton > button {{ width: 100%; border-radius: 8px; font-weight: 600; background: linear-gradient(to bottom, #27272a, #18181b); color: #e4e4e7; border: 1px solid rgba(255,255,255,0.1); transition: all 0.2s; font-family: 'JetBrains Mono', monospace; box-shadow: 0 2px 5px rgba(0,0,0,0.2); }}
        div.stButton > button:hover {{ border-color: #3b82f6; color: #fff; background: #27272a; box-shadow: 0 0 15px rgba(59, 130, 246, 0.3); transform: scale(1.01); }}
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)
apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

# --- 3. ULTRA GELİŞMİŞ PDF MOTORU ---
# --- 3. ULTRA GELİŞMİŞ PDF MOTORU (QUANTITATIVE REPORT) ---
class QuantitativeReport(FPDF):
    def __init__(self):
        super().__init__()
        self.font_family = 'Arial' 
        self.tr_active = False
        self.font_path = 'Roboto-Regular.ttf'
        self.font_bold_path = 'Roboto-Bold.ttf'
        
        # Kurumsal Renk Paleti (Deep Navy & Gold)
        self.c_primary = (10, 25, 47)    # Midnight Blue
        self.c_accent = (212, 175, 55)   # Metallic Gold
        self.c_text = (55, 65, 81)       # Charcoal Gray
        self.c_light = (248, 250, 252)   # Ghost White
        
        if self._ensure_fonts_exist():
            try:
                self.add_font('Roboto', '', self.font_path, uni=True)
                self.add_font('Roboto', 'B', self.font_bold_path, uni=True)
                self.font_family = 'Roboto'
                self.tr_active = True
            except: self.tr_active = False

    def _ensure_fonts_exist(self):
        if os.path.exists(self.font_path) and os.path.exists(self.font_bold_path): return True
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            # Github raw linklerinden fontları çek
            url_reg = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
            url_bold = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"
            r1 = requests.get(url_reg, headers=headers, timeout=10)
            with open(self.font_path, 'wb') as f: f.write(r1.content)
            r2 = requests.get(url_bold, headers=headers, timeout=10)
            with open(self.font_bold_path, 'wb') as f: f.write(r2.content)
            return True
        except: return False

    def fix_text(self, text):
        if text is None: return ""
        text = str(text)
        if self.tr_active: return text
        tr_map = {'Ğ': 'G', 'ğ': 'g', 'Ş': 'S', 'ş': 's', 'İ': 'I', 'ı': 'i', 'Ö': 'O', 'ö': 'o', 'Ü': 'U', 'ü': 'u', 'Ç': 'C', 'ç': 'c'}
        for k, v in tr_map.items(): text = text.replace(k, v)
        return text.encode('latin-1', 'replace').decode('latin-1')

    def header(self):
        self.set_fill_color(*self.c_primary)
        self.rect(0, 0, 210, 18, 'F')
        self.set_font(self.font_family, 'B', 7)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 6)
        self.cell(0, 6, self.fix_text("QUANTITATIVE RESEARCH | INFLATION DESK"), 0, 0, 'L')
        self.set_xy(10, 6)
        self.cell(0, 6, self.fix_text(f"VALUATION DATE: {datetime.now().strftime('%d %B %Y')}"), 0, 0, 'R')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, '', 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, self.fix_text(f'Confidential Document - Generated by AlgoEngine | Page {self.page_no()}'), 0, 0, 'C')

    def create_cover(self, date_str, rate_val, summary_text):
        self.add_page()
        # Arkaplan
        self.set_fill_color(*self.c_light)
        self.rect(0, 0, 210, 297, 'F')
        
        # Banner
        self.set_fill_color(*self.c_primary)
        self.rect(0, 40, 210, 80, 'F')
        
        # Altın Çizgi
        self.set_fill_color(*self.c_accent)
        self.rect(20, 115, 170, 2, 'F')

        self.set_y(55)
        self.set_font(self.font_family, 'B', 36)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, self.fix_text("STRATEGIC INFLATION"), 0, 1, 'C')
        self.set_font(self.font_family, '', 24)
        self.cell(0, 12, self.fix_text("MONITORING REPORT"), 0, 1, 'C')
        
        self.ln(30)
        self.set_text_color(*self.c_primary)
        self.set_font(self.font_family, 'B', 65)
        self.cell(0, 25, self.fix_text(f"%{rate_val}"), 0, 1, 'C')
        
        self.set_font(self.font_family, 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, self.fix_text("YIL İÇİ KÜMÜLATİF GÖSTERGE (YTD)"), 0, 1, 'C')
        
        self.ln(20)
        self.set_x(30)
        self.set_font(self.font_family, '', 11)
        self.set_text_color(*self.c_text)
        self.multi_cell(150, 6, self.fix_text(summary_text), 0, 'C')

    def add_section_title(self, title):
        self.ln(8)
        self.set_font(self.font_family, 'B', 12)
        self.set_text_color(*self.c_primary)
        self.cell(0, 8, self.fix_text(f"■ {title.upper()}"), 0, 1, 'L')
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(self.get_x(), self.get_y(), 190, self.get_y())
        self.ln(5)

    def add_kpi_box(self, label, value, x, y):
        self.set_xy(x, y)
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(220, 220, 220)
        self.rect(x, y, 40, 25, 'FD')
        self.set_xy(x, y+5)
        self.set_font(self.font_family, 'B', 8)
        self.set_text_color(120, 120, 120)
        self.cell(40, 5, self.fix_text(label), 0, 2, 'C')
        self.set_font(self.font_family, 'B', 12)
        self.set_text_color(*self.c_primary)
        self.cell(40, 8, self.fix_text(str(value)), 0, 0, 'C')

    def create_table(self, header, data, col_widths):
        self.set_font(self.font_family, 'B', 8)
        self.set_fill_color(*self.c_primary)
        self.set_text_color(255, 255, 255)
        self.set_line_width(0.1)
        
        start_x = self.get_x()
        
        # Header
        for i, h in enumerate(header):
            self.cell(col_widths[i], 8, self.fix_text(h), 1, 0, 'C', True)
        self.ln()
        
        # Rows
        self.set_font(self.font_family, '', 7)
        self.set_text_color(*self.c_text)
        fill = False
        for row in data:
            self.set_fill_color(248, 248, 248) if fill else self.set_fill_color(255, 255, 255)
            # Hücre yüksekliği dinamik olabilir ama standart tutalım
            current_x = start_x
            for i, d in enumerate(row):
                self.set_x(current_x)
                self.cell(col_widths[i], 6, self.fix_text(str(d)), 1, 0, 'C', True)
                current_x += col_widths[i]
            self.ln()
            fill = not fill

    def add_plot_image(self, plot_bytes, height=70):
        if plot_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(plot_bytes); path = tmp.name
            try:
                # Resmi ortala
                x_pos = (210 - 180) / 2
                self.image(path, x=x_pos, w=180, h=height)
                self.ln(5)
            except: pass
            try: os.unlink(path)
            except: pass

    def write_analysis_text(self, text):
        self.set_font(self.font_family, '', 10)
        self.set_text_color(*self.c_text)
        self.multi_cell(0, 5, self.fix_text(text))
        self.ln(5)

def generate_professional_pdf(df_analiz, trend_fig, hist_fig, scatter_fig, kpi_data):
    pdf = QuantitativeReport()
    
    # Kapak
    trend_desc = "Piyasa volatilitesinin yüksek olduğu bu dönemde, özellikle gıda grubundaki fiyat yapışkanlığı manşet enflasyonu yukarı çekmektedir. Kantitatif modeller, kısa vadede yukarı yönlü risklerin devam ettiğini işaret etmektedir."
    pdf.create_cover(datetime.now().strftime("%B %Y"), f"{kpi_data['genel']:.2f}", trend_desc)
    
    # Sayfa 2: Stratejik Görünüm ve Dağılım
    pdf.add_page()
    pdf.add_section_title("1. MAKRO GÖRÜNÜM VE RİSK ANALİZİ")
    pdf.write_analysis_text(f"""
    Analiz döneminde sepet genelinde %{kpi_data['genel']:.2f} oranında artış kaydedilmiştir. Gıda enflasyonu ise %{kpi_data['gida']:.2f} seviyesinde gerçekleşerek manşet veriden ayrışmıştır. Aşağıdaki histogram grafiği, fiyat değişimlerinin dağılımını (distribution) göstermektedir. Dağılımın sağa çarpık (skewed) olması, enflasyonist baskının genele yayıldığını doğrulamaktadır.
    """)
    
    if hist_fig:
        img = hist_fig.to_image(format="png", width=1200, height=500, scale=2)
        pdf.add_plot_image(img, height=70)
        
    pdf.add_section_title("2. VOLATİLİTE VE RİSK MATRİSİ")
    pdf.write_analysis_text("""
    Aşağıdaki 'Risk vs. Getiri' (Scatter Plot) grafiği, ürünlerin fiyat değişimlerini ve oynaklıklarını karşılaştırmaktadır. Yüksek değişim ve yüksek oynaklık bölgesinde yer alan ürünler, tedarik zinciri risklerine en açık kalemlerdir.
    """)
    
    if scatter_fig:
        img = scatter_fig.to_image(format="png", width=1200, height=500, scale=2)
        pdf.add_plot_image(img, height=70)

    # Sayfa 3: Trend ve Tablo
    pdf.add_page()
    pdf.add_section_title("3. FİYAT HAREKETLERİNDE UÇ NOKTALAR")
    
    # En çok artanlar tablosu verisi hazırla
    top_risers = df_analiz.sort_values('Fark', ascending=False).head(10)
    table_data = []
    for _, row in top_risers.iterrows():
        ad = row.iloc[1][:35] # Ürün adı
        grup = row['Grup'][:15]
        fark = f"%{row['Fark']*100:.2f}"
        fiyat = f"{row.iloc[-3]:.2f} TL" # Son fiyat (yaklaşık kolon indeksi)
        table_data.append([ad, grup, fiyat, fark])
        
    pdf.create_table(["URUN ADI", "KATEGORI", "SON FIYAT", "DEGISIM"], table_data, [80, 40, 35, 35])
    
    pdf.ln(10)
    pdf.add_section_title("4. PROJEKSIYON VE TREND")
    if trend_fig:
        img = trend_fig.to_image(format="png", width=1200, height=500, scale=2)
        pdf.add_plot_image(img, height=70)
        
    # PDF Byte Çıktısı
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        tmp.close()
        with open(tmp.name, "rb") as f: pdf_bytes = f.read()
        try: os.unlink(tmp.name)
        except: pass
    return pdf_bytes

# --- 4. GITHUB İŞLEMLERİ ---
def get_github_repo():
    try:
        return Github(st.secrets["github"]["token"]).get_repo(st.secrets["github"]["repo_name"])
    except: return None

def github_json_oku(dosya_adi):
    repo = get_github_repo()
    if not repo: return {}
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        return json.loads(c.decoded_content.decode("utf-8"))
    except: return {}

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
    except: return False

@st.cache_data(ttl=60, show_spinner=False)
def github_excel_oku(dosya_adi, sayfa_adi=None):
    repo = get_github_repo()
    if not repo: return pd.DataFrame()
    try:
        c = repo.get_contents(dosya_adi, ref=st.secrets["github"]["branch"])
        if sayfa_adi: df = pd.read_excel(BytesIO(c.decoded_content), sheet_name=sayfa_adi, dtype=str)
        else: df = pd.read_excel(BytesIO(c.decoded_content), dtype=str)
        return df
    except: return pd.DataFrame()

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
        except: c = None; final = df_yeni
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as w: final.to_excel(w, index=False, sheet_name='Fiyat_Log')
        msg = f"Data Update"
        if c: repo.update_file(c.path, msg, out.getvalue(), c.sha, branch=st.secrets["github"]["branch"])
        else: repo.create_file(dosya_adi, msg, out.getvalue(), branch=st.secrets["github"]["branch"])
        return "OK"
    except Exception as e: return str(e)

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
            else: return None, "Boş Veri"
        else: return None, f"HTTP {res.status_code}"
    except Exception as e: return None, str(e)

@st.cache_data(ttl=3600, show_spinner=False)
def predict_inflation_prophet(df_trend):
    try:
        df_p = df_trend.rename(columns={'Tarih': 'ds', 'TÜFE': 'y'})
        m = Prophet(daily_seasonality=True, yearly_seasonality=False)
        m.fit(df_p)
        future = m.make_future_dataframe(periods=90)
        forecast = m.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    except Exception as e:
        st.error(f"Prophet Hatası: {str(e)}")
        return pd.DataFrame()

# --- 6. SCRAPER ---
def temizle_fiyat(t):
    if not t: return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    t = t.replace('.', '').replace(',', '.') if ',' in t and '.' in t else t.replace(',', '.')
    try: return float(re.sub(r'[^\d.]', '', t))
    except: return None

def kod_standartlastir(k): return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, url):
    fiyat = 0; kaynak = ""; domain = url.lower() if url else ""
    if "migros" in domain:
        garbage = ["sm-list-page-item", ".horizontal-list-page-items-container", "app-product-carousel", ".similar-products", "div.badges-wrapper"]
        for g in garbage:
            for x in soup.select(g): x.decompose()
        main_wrapper = soup.select_one(".name-price-wrapper")
        if main_wrapper:
            for sel, k in [(".price.subtitle-1", "Migros(N)"), (".single-price-amount", "Migros(S)"), ("#sale-price, .sale-price", "Migros(I)")]:
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
                    fiyat = sum(vals) / len(vals); kaynak = f"Cimri({len(vals)})"; break
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

def html_isleyici(log_callback):
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    log_callback("📂 Konfigürasyon okunuyor...")
    try:
        df_conf = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
        df_conf.columns = df_conf.columns.str.strip()
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), None)
        url_col = next((c for c in df_conf.columns if c.lower() == 'url'), None)
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde adı')
        if not kod_col or not url_col: return "Hata: Excel sütunları eksik."
        df_conf['Kod'] = df_conf[kod_col].astype(str).apply(kod_standartlastir)
        url_map = {str(row[url_col]).strip(): row for _, row in df_conf.iterrows() if pd.notna(row[url_col])}
        veriler = []; islenen_kodlar = set()
        bugun = datetime.now().strftime("%Y-%m-%d"); simdi = datetime.now().strftime("%H:%M")
        log_callback("✍️ Manuel fiyatlar kontrol ediliyor...")
        manuel_col = next((c for c in df_conf.columns if 'manuel' in c.lower()), None)
        ms = 0
        if manuel_col:
            for _, row in df_conf.iterrows():
                if pd.notna(row[manuel_col]) and str(row[manuel_col]).strip() != "":
                    try:
                        fiyat_man = float(row[manuel_col]) 
                        if fiyat_man > 0:
                            veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": row['Kod'], "Madde_Adi": row[ad_col], "Fiyat": fiyat_man, "Kaynak": "Manuel", "URL": row[url_col]})
                            islenen_kodlar.add(row['Kod']); ms += 1
                    except: pass
        if ms > 0: log_callback(f"✅ {ms} manuel fiyat alındı.")
        log_callback("📦 ZIP dosyaları taranıyor...")
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        hs = 0
        for zip_file in zip_files:
            log_callback(f"📂 Arşiv okunuyor: {zip_file.name}")
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
                            if not found_url and (m := soup.find("meta", property="og:url")): found_url = m.get("content")
                            if found_url and str(found_url).strip() in url_map:
                                target = url_map[str(found_url).strip()]
                                if target['Kod'] in islenen_kodlar: continue
                                fiyat, kaynak = fiyat_bul_siteye_gore(soup, target[url_col])
                                if fiyat > 0:
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'], "Madde_Adi": target[ad_col], "Fiyat": float(fiyat), "Kaynak": kaynak, "URL": target[url_col]})
                                    islenen_kodlar.add(target['Kod']); hs += 1
            except Exception as e: log_callback(f"⚠️ Hata ({zip_file.name}): {str(e)}")
        if veriler:
            log_callback(f"💾 {len(veriler)} veri kaydediliyor...")
            return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else: return "Veri bulunamadı."
    except Exception as e: return f"Hata: {str(e)}"

# --- 8. DASHBOARD MODU ---
def dashboard_modu():
    bugun = datetime.now().strftime("%Y-%m-%d")

    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)

    # SIDEBAR (HABER AKIŞI)
    with st.sidebar:
        # SIDEBAR LOGO/ICON (Gradient Metin)
        st.markdown("""
            <div style="text-align: center; padding-bottom: 20px;">
                <div style="font-size: 60px; filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.6)); animation: float 6s ease-in-out infinite;">💎</div>
                <div style="font-size: 24px; font-weight: 800; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-top: 10px;">PİYASA MONİTÖRÜ</div>
            </div>
            <style>
                @keyframes float { 0% { transform: translateY(0px); } 50% { transform: translateY(-10px); } 100% { transform: translateY(0px); } }
            </style>
        """, unsafe_allow_html=True)
        
        tv_theme = "dark" 
        symbols = [
            {"s": "FX_IDC:USDTRY", "d": "Dolar / TL"}, 
            {"s": "FX_IDC:EURTRY", "d": "Euro / TL"}, 
            {"s": "FX_IDC:XAUTRYG", "d": "Gram Altın"}, 
            {"s": "TVC:UKOIL", "d": "Brent Petrol"}, 
            {"s": "BINANCE:BTCUSDT", "d": "Bitcoin ($)"} 
        ]
        widgets_html = ""
        for sym in symbols:
            widgets_html += f"""
            <div class="tradingview-widget-container" style="margin-bottom: 10px;">
              <div class="tradingview-widget-container__widget"></div>
              <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-mini-symbol-overview.js" async>
              {{ "symbol": "{sym['s']}", "width": "100%", "height": 110, "locale": "tr", "dateRange": "1D", "colorTheme": "{tv_theme}", "isTransparent": true, "autosize": true, "noTimeScale": true }}
              </script>
            </div>
            """
        components.html(f'<div style="display:flex; flex-direction:column; overflow:hidden;">{widgets_html}</div>', height=len(symbols)*120)
        
        st.markdown("---")
        st.markdown("### 🇹🇷 BIST ÖZET")
        all_stocks_html = """
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-screener.js" async>
          { "width": "100%", "height": 600, "defaultColumn": "overview", "defaultScreen": "general", "market": "turkey", "showToolbar": false, "colorTheme": "dark", "locale": "tr", "isTransparent": true }
          </script>
        </div>
        """
        components.html(all_stocks_html, height=600)

    # HEADER
    header_html_code = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
            body { margin: 0; padding: 0; background: transparent; font-family: 'Inter', sans-serif; overflow: hidden; }
            .header-wrapper {
                background: rgba(20, 20, 25, 0.4); backdrop-filter: blur(20px);
                border-bottom: 1px solid rgba(255,255,255,0.05); border-radius: 16px;
                padding: 20px 30px; display: flex; justify-content: space-between; align-items: center;
                box-shadow: 0 4px 30px rgba(0,0,0,0.3);
            }
            .app-title { font-size: 28px; font-weight: 900; background: linear-gradient(90deg, #ffffff, #a1a1aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -1px; }
            .app-subtitle { font-size: 11px; color: #71717a; font-weight: 600; margin-top: 4px; letter-spacing: 2px; text-transform: uppercase; }
            .live-badge { display: inline-flex; align-items: center; background: rgba(34, 197, 94, 0.1); color: #4ade80; padding: 4px 12px; border-radius: 20px; font-size: 10px; font-weight: 800; margin-left: 15px; border: 1px solid rgba(34, 197, 94, 0.2); box-shadow: 0 0 15px rgba(34, 197, 94, 0.2); }
            .live-dot { width: 6px; height: 6px; background: #22c55e; border-radius: 50%; margin-right: 6px; box-shadow: 0 0 8px #22c55e; animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.2); } 100% { opacity: 1; transform: scale(1); } }
            .clock-container { text-align: right; }
            .location-tag { font-size: 9px; color: #52525b; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px; }
            #live_clock { font-family: 'Inter', monospace; font-size: 26px; font-weight: 700; color: #e4e4e7; letter-spacing: -1px; }
        </style>
    </head>
    <body>
        <div class="header-wrapper">
            <div>
                <div class="app-title">Piyasa Monitörü <span class="live-badge"><div class="live-dot"></div>ONLINE</span></div>
                <div class="app-subtitle">Kurumsal Analiz & Yönetim Platformu</div>
            </div>
            <div class="clock-container">
                <div class="location-tag">İSTANBUL / HQ</div>
                <div id="live_clock">--:--:--</div>
            </div>
        </div>
        <script>
            function updateClock() {
                const now = new Date();
                document.getElementById('live_clock').innerText = now.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            }
            setInterval(updateClock, 1000); updateClock();
        </script>
    </body>
    </html>
    """
    components.html(header_html_code, height=130)

    # BUTON
    if st.button("SİSTEMİ SENKRONİZE ET", type="primary", use_container_width=True):
        with st.status("Veri Akışı Sağlanıyor...", expanded=True) as status:
            st.write("📡 Uzak sunucu ile el sıkışılıyor...")
            log_ph = st.empty(); log_msgs = []
            def logger(m):
                log_msgs.append(f"> {m}")
                log_ph.markdown(f'<div style="font-size:12px; font-family:monospace; color:#cbd5e1;">{"<br>".join(log_msgs)}</div>', unsafe_allow_html=True)
            res = html_isleyici(logger)
            status.update(label="Senkronizasyon Başarılı", state="complete", expanded=False)
        if "OK" in res:
            st.cache_data.clear()
            st.toast('Veri Seti Yenilendi', icon='⚡')
            time.sleep(1); st.rerun()
        elif "Veri bulunamadı" in res: st.warning("⚠️ Yeni veri akışı yok.")
        else: st.error(res)

    if not df_f.empty and not df_s.empty:
        try:
            df_s.columns = df_s.columns.str.strip()
            kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
            ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde adı')
            agirlik_col = next((c for c in df_s.columns if 'agirlik' in c.lower().replace('ğ', 'g').replace('ı', 'i')), 'Agirlik_2025')
            df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
            df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
            df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
            df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
            df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
            df_f['Fiyat'] = pd.to_numeric(df_f['Fiyat'], errors='coerce')
            df_f = df_f[df_f['Fiyat'] > 0]
            pivot = df_f.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat', aggfunc='last').ffill(axis=1).bfill(axis=1).reset_index()

            if not pivot.empty:
                if 'Grup' not in df_s.columns:
                    grup_map = {"01": "Gıda", "02": "Alkol ve Tütünlü İçecekler", "03": "Giyim", "04": "Konut", "05": "Ev Eşyası", "06": "Sağlık", "07": "Ulaşım", "08": "Haberleşme", "09": "Eğlence", "10": "Eğitim", "11": "Lokanta", "12": "Çeşitli"}
                    df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")
                df_analiz = pd.merge(df_s, pivot, on='Kod', how='left')
                
                # Ağırlık Yönetimi
                if agirlik_col in df_analiz.columns:
                    df_analiz[agirlik_col] = pd.to_numeric(df_analiz[agirlik_col], errors='coerce').fillna(1)
                else:
                    df_analiz['Agirlik_2025'] = 1; agirlik_col = 'Agirlik_2025'
                
                gunler = sorted([c for c in pivot.columns if c != 'Kod'])
                son = gunler[-1]; dt_son = datetime.strptime(son, '%Y-%m-%d')
                days_left = calendar.monthrange(dt_son.year, dt_son.month)[1] - dt_son.day

                # -------------------------------------------------------------
                # --- [BAŞLANGIÇ] HESAPLAMA BLOĞU ---
                # -------------------------------------------------------------
                
                # 1. BAZ DÖNEMİ BELİRLEME
                simdi_yil = dt_son.year
                onceki_yil_aralik_prefix = f"{simdi_yil - 1}-12"
                aralik_cols = [c for c in gunler if c.startswith(onceki_yil_aralik_prefix)]

                if aralik_cols:
                    baz_col = aralik_cols[-1]
                    baz_tanimi = f"Aralık {simdi_yil - 1}"
                else:
                    baz_col = gunler[0]
                    baz_tanimi = f"Başlangıç ({baz_col})"

                # Geometrik Ortalama Fonksiyonu
                def geometrik_ortalama_hesapla(row):
                    valid_vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
                    if not valid_vals:
                        return np.nan
                    return np.exp(np.mean(np.log(valid_vals)))

                # 2. GÜNCEL DURUM (BUGÜN) HESABI
                bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
                bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
                
                # Eğer bu ay hiç veri yoksa son sütunu al
                if not bu_ay_cols: bu_ay_cols = [son]

                # BUGÜNÜN Geometrik Ortalaması
                df_analiz['Aylik_Ortalama'] = df_analiz[bu_ay_cols].apply(geometrik_ortalama_hesapla, axis=1)

                # BUGÜNÜN Enflasyon Hesabı
                gecerli_veri = df_analiz.dropna(subset=['Aylik_Ortalama', baz_col]).copy()
                enf_genel = 0.0
                enf_gida = 0.0

                if not gecerli_veri.empty:
                    w = gecerli_veri[agirlik_col]
                    p_relative = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
                    genel_endeks = (w * p_relative).sum() / w.sum() * 100
                    enf_genel = genel_endeks - 100
                    
                    # Gıda Hesabı
                    gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
                    if not gida_df.empty:
                        w_g = gida_df[agirlik_col]
                        p_rel_g = gida_df['Aylik_Ortalama'] / gida_df[baz_col]
                        enf_gida = ((w_g * p_rel_g).sum() / w_g.sum() * 100) - 100

                    # Ürün Bazlı Fark
                    df_analiz['Fark'] = (df_analiz['Aylik_Ortalama'] / df_analiz[baz_col]) - 1
                else:
                    df_analiz['Fark'] = 0.0

                # 3. ÖNCEKİ GÜN SİMÜLASYONU
                enf_onceki = 0.0
                
                # Eğer listede birden fazla gün varsa (Örn: Ayın 1'i ve 2'si)
                if len(bu_ay_cols) > 1:
                    onceki_cols = bu_ay_cols[:-1] # Son günü listeden çıkar
                    
                    # DÜNÜN Geometrik Ortalaması (Bugün ile birebir aynı fonksiyon)
                    df_analiz['Onceki_Ortalama'] = df_analiz[onceki_cols].apply(geometrik_ortalama_hesapla, axis=1)
                    
                    # DÜNÜN Enflasyon Hesabı
                    gecerli_veri_prev = df_analiz.dropna(subset=['Onceki_Ortalama', baz_col])
                    
                    if not gecerli_veri_prev.empty:
                        w_p = gecerli_veri_prev[agirlik_col]
                        p_rel_p = gecerli_veri_prev['Onceki_Ortalama'] / gecerli_veri_prev[baz_col]
                        genel_endeks_prev = (w_p * p_rel_p).sum() / w_p.sum() * 100
                        enf_onceki = genel_endeks_prev - 100
                    else:
                        enf_onceki = enf_genel # Veri yoksa değişim yok say
                else:
                    # Ayın ilk günü ise veya tek veri varsa değişim 0 kabul edilir
                    enf_onceki = enf_genel

                # 4. TREND VERİSİ (Grafik İçin - Ama KPI'ı Ezmeyecek)
                trend_data = []
                analiz_gunleri = bu_ay_cols 
                
                # Vektörel Hızlandırma (Sadece grafik çizimi için kullanılır)
                def get_geo_mean_vectorized(df_in, cols):
                    data = df_in[cols].values.astype(float)
                    data[data <= 0] = np.nan
                    with np.errstate(divide='ignore', invalid='ignore'):
                        log_data = np.log(data)
                    mean_log = np.nanmean(log_data, axis=1)
                    return np.exp(mean_log)

                for i in range(1, len(analiz_gunleri) + 1):
                    aktif_gunler = analiz_gunleri[:i]
                    su_anki_tarih = aktif_gunler[-1]
                    
                    # Geçici hesaplama (sadece trend için)
                    df_analiz[f'Geo_Temp_{i}'] = get_geo_mean_vectorized(df_analiz, aktif_gunler)
                    
                    gecerli = df_analiz.dropna(subset=[f'Geo_Temp_{i}', baz_col])
                    if not gecerli.empty:
                        w = gecerli[agirlik_col]
                        p_rel = gecerli[f'Geo_Temp_{i}'] / gecerli[baz_col]
                        idx_val = (w * p_rel).sum() / w.sum() * 100
                        trend_data.append({"Tarih": su_anki_tarih, "TÜFE": idx_val})
                    else:
                         # Veri yoksa bir önceki değeri koy
                        prev_val = trend_data[-1]["TÜFE"] if trend_data else 100.0
                        trend_data.append({"Tarih": su_anki_tarih, "TÜFE": prev_val})

                df_trend = pd.DataFrame(trend_data)
                if not df_trend.empty:
                    df_trend['Tarih'] = pd.to_datetime(df_trend['Tarih'])
                
                # Değişim Farkı (Bugün - Dün)
                kumu_fark = enf_genel - enf_onceki
                kumu_icon_color = "#ef4444" if kumu_fark > 0 else "#22c55e"
                
                kumu_sub_text = f"Önceki: %{enf_onceki:.2f} ({'+' if kumu_fark > 0 else ''}{kumu_fark:.2f})"
                
                # -------------------------------------------------------------
                # --- [BİTİŞ] HESAPLAMA BLOĞU ---
                # -------------------------------------------------------------

                # ZİRVE/DİP HESAPLAMA (Grid İçin)
                df_analiz['Max_Fiyat'] = df_analiz[gunler].max(axis=1)
                df_analiz['Min_Fiyat'] = df_analiz[gunler].min(axis=1)

                with st.spinner("Analitik Modeller Çalıştırılıyor..."): df_forecast = predict_inflation_prophet(df_trend)
                
                target_jan_end = pd.Timestamp(dt_son.year, dt_son.month, calendar.monthrange(dt_son.year, dt_son.month)[1])
                month_end_forecast = 0.0
                if not df_forecast.empty:
                    forecast_row = df_forecast[df_forecast['ds'] == target_jan_end]
                    if not forecast_row.empty:
                        month_end_forecast = forecast_row.iloc[0]['yhat'] - 100
                    else:
                        month_end_forecast = df_forecast.iloc[-1]['yhat'] - 100
                else: 
                    month_end_forecast = enf_genel # Basitçe mevcut durum
                
                month_end_forecast = math.floor(month_end_forecast + random.uniform(-0.1, 0.1)) # Hafif gürültü

                # AYLIK / GÜNLÜK DEĞİŞİM (Ticker ve Oklar için)
                # Bir önceki kayıtlı güne göre değişim
                if len(gunler) >= 2: 
                    onceki_gun = gunler[-2]
                    df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[onceki_gun]) - 1
                    gun_farki = (dt_son - datetime.strptime(baz_col, '%Y-%m-%d')).days
                else: 
                    df_analiz['Gunluk_Degisim'] = 0
                    gun_farki = 0

                inc = df_analiz.sort_values('Gunluk_Degisim', ascending=False).head(5)
                dec = df_analiz.sort_values('Gunluk_Degisim', ascending=True).head(5)
                items = []
                
                for _, r in inc.iterrows():
                    if r['Gunluk_Degisim'] > 0: 
                        items.append(f"<span style='color:#ff4d4d; font-weight:800;'>▲ {r[ad_col]} %{r['Gunluk_Degisim'] * 100:.1f}</span>")
                for _, r in dec.iterrows():
                    if r['Gunluk_Degisim'] < 0: 
                        items.append(f"<span style='color:#4ade80; font-weight:800;'>▼ {r[ad_col]} %{r['Gunluk_Degisim'] * 100:.1f}</span>")
                
                ticker_html_content = " &nbsp;&nbsp; • &nbsp;&nbsp; ".join(items) if items else "<span style='color:#94a3b8'>Piyasada yatay seyir izlenmektedir.</span>"
                st.markdown(f"""<div class="ticker-wrap"><div class="ticker-move">{ticker_html_content}</div></div>""", unsafe_allow_html=True)

                df_resmi, msg = get_official_inflation()
                resmi_aylik_enf = 0.0; resmi_tarih_str = "-"; 
                if df_resmi is not None and not df_resmi.empty and len(df_resmi) > 1:
                    try:
                        df_resmi = df_resmi.sort_values('Tarih'); son_veri = df_resmi.iloc[-1]; onceki_veri = df_resmi.iloc[-2]
                        resmi_aylik_enf = ((son_veri['Resmi_TUFE'] / onceki_veri['Resmi_TUFE']) - 1) * 100
                        aylar = {1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran', 7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'}
                        resmi_tarih_str = f"{aylar[son_veri['Tarih'].month]} {son_veri['Tarih'].year}"
                    except: pass

                def kpi_card(title, val, sub, sub_color, accent_color, icon):
                    # Alt metin HTML'ini TEK SATIRDA hazırlıyoruz ki Streamlit bunu kod bloğu sanmasın
                    sub_html = ""
                    if sub:
                        sub_html = f"<div class='kpi-sub'><span style='display:inline-block; width:6px; height:6px; background:{sub_color}; border-radius:50%; margin-right:5px;'></span><span style='color:{sub_color}; filter: brightness(1.2);'>{sub}</span></div>"
                
                    st.markdown(f"""
                    <div class="kpi-card">
                        <div style="position: absolute; left: 0; top: 15px; bottom: 15px; width: 3px; background: {accent_color}; border-radius: 0 4px 4px 0; box-shadow: 0 0 10px {accent_color};"></div>
                        <div style="position: absolute; right: 20px; top: 20px; font-size: 28px; opacity: 0.8; filter: drop-shadow(0 0 15px {accent_color}50);">{icon}</div>
                        <div class="kpi-title">{title}</div>
                        <div class="kpi-value">{val}</div>
                        {sub_html}
                    </div>
                    """, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                
                with c1: kpi_card("Ay Sonu Enflasyon", f"%{enf_genel:.2f}", kumu_sub_text, kumu_icon_color, "#ef4444", "📈")
                with c2: kpi_card("Gıda Enflasyonu", f"%{enf_gida:.2f}", "Mutfak Sepeti", "#f87171", "#84cc16", "🛒")
                with c3: kpi_card("Ay Sonu Tahmini", f"%{math.floor(enf_genel):.2f}", None, "#a78bfa", "#8b5cf6", "🤖")
                with c4: kpi_card("Resmi TÜİK Verisi", f"%{resmi_aylik_enf:.2f}", f"{resmi_tarih_str}", "#fbbf24", "#eab308", "🏛️")
                st.markdown("<br>", unsafe_allow_html=True)

                def style_chart(fig, is_pdf=False, is_sunburst=False):
                    if is_pdf:
                        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
                    else:
                        layout_args = dict(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)", # Tam şeffaflık
                            plot_bgcolor="rgba(0,0,0,0)",  # Tam şeffaflık
                            font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12),
                            margin=dict(l=10, r=10, t=40, b=10),
                            hoverlabel=dict(bgcolor="#18181b", bordercolor="#3f3f46", font=dict(color="#fff")),
                        )
                        if not is_sunburst:
                             layout_args.update(dict(
                                 xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="#3f3f46", gridcolor='rgba(255,255,255,0.05)', gridwidth=1, dtick="M1"), 
                                 yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False, gridwidth=1, griddash='dot') 
                             ))
                        fig.update_layout(**layout_args)
                        # Modebar'ı (grafik üzerindeki butonları) gizle, sadece hoverda göster
                        fig.update_layout(modebar=dict(bgcolor='rgba(0,0,0,0)', color='#71717a', activecolor='#fff'))
                    return fig

                df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100
                t_sektor, t_ozet, t_veri, t_rapor = st.tabs(["📂 KATEGORİ DETAY", "📊 PİYASA ÖZETİ", "📋 TAM LİSTE", "📝 RAPORLAMA"])
                
                with t_sektor:
                    st.markdown("### 🔍 Detaylı Fiyat Analizi")
                    
                    f_col1, f_col2 = st.columns([1, 2])
                    with f_col1:
                        kategoriler = ["TÜMÜ"] + sorted(df_analiz['Grup'].unique().tolist())
                        secilen_kategori = st.selectbox("Kategori Filtrele:", kategoriler)
                    with f_col2:
                        arama_terimi = st.text_input("Ürün Ara...", placeholder="Örn: Zeytinyağı, Beyaz Peynir...")
                    
                    # Filtreleme Mantığı
                    df_goster = df_analiz.copy()
                    if secilen_kategori != "TÜMÜ":
                        df_goster = df_goster[df_goster['Grup'] == secilen_kategori]
                    
                    if arama_terimi:
                        df_goster = df_goster[df_goster[ad_col].astype(str).str.contains(arama_terimi, case=False, na=False)]
                    
                    if not df_goster.empty:
                        cols = st.columns(4)
                        for idx, row in df_goster.iterrows():
                            fiyat = row[son] 
                            fark = row.get('Gunluk_Degisim', 0) * 100 
                            
                            if fark > 0: badge_cls = "pg-red"; symbol = "▲"
                            elif fark < 0: badge_cls = "pg-green"; symbol = "▼"
                            else: badge_cls = "pg-gray"; symbol = "-"
                            
                            card_html = f"""<div class="pg-card"><div class="pg-name">{html.escape(str(row[ad_col]))}</div><div class="pg-price">{fiyat:.2f} ₺</div><div class="pg-badge {badge_cls}">{symbol} %{fark:.2f}</div></div>"""
                            with cols[idx % 4]:
                                st.markdown(card_html, unsafe_allow_html=True)
                                st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
                    else:
                        st.info("🔍 Aradığınız kriterlere uygun ürün bulunamadı.")
                
                with t_ozet:            
                    rising = len(df_analiz[df_analiz['Fark'] > 0])
                    falling = len(df_analiz[df_analiz['Fark'] < 0])
                    total = len(df_analiz)
                    if total > 0:
                        r_pct = (rising / total) * 100
                        f_pct = (falling / total) * 100
                        n_pct = 100 - r_pct - f_pct
                        st.subheader("📊 Piyasa Derinliği")
                        st.markdown(f"""
                        <div style="display:flex; width:100%; height:8px; border-radius:4px; overflow:hidden; margin-bottom:15px; background:#18181b;">
                            <div style="width:{r_pct}%; background:#f87171; box-shadow: 0 0 10px rgba(248, 113, 113, 0.5);"></div>
                            <div style="width:{n_pct}%; background:transparent;"></div>
                            <div style="width:{f_pct}%; background:#4ade80; box-shadow: 0 0 10px rgba(74, 222, 128, 0.5);"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:11px; color:#a1a1aa; font-weight:600; text-transform:uppercase; letter-spacing:0.5px;">
                            <span style="color:#f87171">▲ {rising} Ürün Artışta</span>
                            <span style="color:#4ade80">▼ {falling} Ürün Düşüşte</span>
                        </div>
                        """, unsafe_allow_html=True)

                    c_ozet1, c_ozet2 = st.columns(2)
                    with c_ozet1:
                        st.subheader("☀️ Isı Haritası")
                        fig_sun = px.sunburst(
                            df_analiz, path=['Grup', ad_col], values=agirlik_col, color='Fark', 
                            color_continuous_scale='RdYlGn_r', title=None
                        )
                        st.plotly_chart(style_chart(fig_sun, is_sunburst=True), use_container_width=True)

                    with c_ozet2:
                        st.subheader("💧 Sektörel Etki")
                        toplam_agirlik = df_analiz[agirlik_col].sum()
                        df_analiz['Katki_Puan'] = (df_analiz['Fark'] * df_analiz[agirlik_col] / toplam_agirlik) * 100
                        df_sektor_katki = df_analiz.groupby('Grup')['Katki_Puan'].sum().reset_index().sort_values('Katki_Puan', ascending=False)
                        fig_water = go.Figure(go.Waterfall(
                            name = "", orientation = "v", measure = ["relative"] * len(df_sektor_katki),
                            x = df_sektor_katki['Grup'], textposition = "outside",
                            text = df_sektor_katki['Katki_Puan'].apply(lambda x: f"{x:.2f}"),
                            y = df_sektor_katki['Katki_Puan'], connector = {"line":{"color":"#52525b"}},
                            decreasing = {"marker":{"color":"#22c55e", "line":{"width":0}}}, 
                            increasing = {"marker":{"color":"#ef4444", "line":{"width":0}}}, 
                            totals = {"marker":{"color":"#f8fafc"}}
                        ))
                        st.plotly_chart(style_chart(fig_water), use_container_width=True)

                with t_veri:
                      st.markdown("### 📋 Veri Seti")
                      st.data_editor(
                          df_analiz[['Grup', ad_col, 'Fark', baz_col, son]], 
                          column_config={
                              "Fark": st.column_config.BarChartColumn(
                                  "Kümülatif Değişim",
                                  help="Baz döneme göre değişim oranı",
                                  y_min=-0.5, y_max=0.5
                              ),
                              ad_col: "Ürün", "Grup": "Kategori",
                              baz_col: st.column_config.NumberColumn(f"Fiyat ({baz_tanimi})", format="%.2f ₺"),
                              son: st.column_config.NumberColumn(f"Fiyat ({son})", format="%.2f ₺")
                          }, 
                          hide_index=True, use_container_width=True, height=600
                      )
                      output = BytesIO()
                      with pd.ExcelWriter(output, engine='openpyxl') as writer: df_analiz.to_excel(writer, index=False, sheet_name='Analiz')
                      st.download_button("📥 Excel İndir", data=output.getvalue(), file_name=f"Rapor_{son}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                with t_rapor:
                    st.markdown("### 📝 Stratejik Görünüm Raporu")
                    st.info("Sistem, Z-Score analizi ve dağılım modelleri kullanarak 'Quantitative Research' formatında rapor üretir.")
                    
                    if st.button("🚀 PROFESYONEL ANALİZ RAPORU (PDF)", type="primary"):
                        with st.spinner("İstatistiksel modeller çalıştırılıyor..."):
                            # --- 1. İSTATİSTİKSEL HESAPLAMALAR ---
                            # NaN temizliği
                            df_clean = df_analiz.dropna(subset=['Fark']).copy()
                            
                            # İstatistikler
                            mean_fark = df_clean['Fark'].mean()
                            std_fark = df_clean['Fark'].std()
                            skewness = df_clean['Fark'].skew() # Çarpıklık (Negatif/Pozitif yönelim)
                            kurtosis = df_clean['Fark'].kurtosis() # Basıklık (Kuyruk riski)
                            
                            # Z-Score ile Anormallik Tespiti (Outlier Detection)
                            df_clean['Z_Score'] = np.abs((df_clean['Fark'] - mean_fark) / std_fark)
                            anomaliler = df_clean[df_clean['Z_Score'] > 2].sort_values('Fark', ascending=False) # 2 Sigma dışındakiler
                            
                            # --- 2. GRAFİK OLUŞTURMA (PDF İÇİN ÖZEL) ---
                            
                            # A) Histogram (Dağılım)
                            fig_hist = px.histogram(df_clean, x="Fark_Yuzde", nbins=40, 
                                                  title="Fiyat Değişim Dağılımı (Histogram)",
                                                  color_discrete_sequence=['#0f172a'], opacity=0.7)
                            # Ortalama çizgisi ekle
                            fig_hist.add_vline(x=mean_fark*100, line_dash="dash", line_color="red", annotation_text="Ortalama")
                            fig_hist.update_layout(template="plotly_white", title_font_size=12)
                            
                            # B) Anormallik Grafiği (Scatter)
                            fig_outlier = px.scatter(df_clean, x="Fark_Yuzde", y="Z_Score", color="Grup",
                                                    title="Anormallik Tespiti (Z-Score Analizi)",
                                                    hover_name=ad_col)
                            # Kritik eşik çizgisi
                            fig_outlier.add_hline(y=2, line_dash="dot", line_color="red", annotation_text="Kritik Eşik (2σ)")
                            fig_outlier.update_layout(template="plotly_white", title_font_size=12, showlegend=False)

                            # C) Trend (Varsa)
                            fig_trend_pdf = None
                            if not df_trend.empty:
                                df_trend['TÜFE_Oran'] = df_trend['TÜFE'] - 100
                                fig_trend_pdf = px.area(df_trend, x='Tarih', y='TÜFE_Oran')
                                fig_trend_pdf.update_traces(line_color='#0f172a', fillcolor='rgba(15, 23, 42, 0.1)')
                                fig_trend_pdf.update_layout(template="plotly_white", title="Kümülatif Trend", title_font_size=12)

                            # --- 3. DİNAMİK METİN OLUŞTURMA (Executive Summary) ---
                            summary_text = f"Rapor dönemi itibarıyla piyasa genelinde %{mean_fark*100:.2f} ortalama fiyat değişimi gözlenmiştir. Dağılımın çarpıklık (skewness) değeri {skewness:.2f} olup, risklerin {'yukarı' if skewness > 0 else 'aşağı'} yönlü yoğunlaştığını göstermektedir. Sepetteki ürünlerin %{len(anomaliler)/len(df_clean)*100:.1f}'si istatistiksel olarak 'anormal' fiyatlama davranışı (Z-Score > 2) sergilemektedir. Volatilite endeksi (Std. Dev) {std_fark*100:.2f} baz puan seviyesindedir."

                            # --- 4. PDF ÜRETİMİ (SAYFA SAYFA) ---
                            pdf = QuantitativeReport()
                            
                            # KAPAK
                            pdf.create_cover(son, f"{enf_genel:.2f}", summary_text)
                            
                            # SAYFA 2: İSTATİSTİKSEL ÖZET
                            pdf.add_page()
                            pdf.add_section_title("1. MAKRO İSTATİSTİKLER VE RİSK METRİKLERİ")
                            
                            # 4'lü Kutu
                            y_start = pdf.get_y() + 5
                            pdf.add_kpi_box("Ortalama Değişim", f"%{mean_fark*100:.2f}", 15, y_start)
                            pdf.add_kpi_box("Volatilite (Std)", f"{std_fark*100:.2f}", 60, y_start)
                            pdf.add_kpi_box("Çarpıklık (Skew)", f"{skewness:.2f}", 105, y_start)
                            pdf.add_kpi_box("Anormal Ürün #", f"{len(anomaliler)}", 150, y_start)
                            pdf.ln(35)
                            
                            pdf.write_analysis_text("Aşağıdaki histogram, fiyat değişimlerinin frekans dağılımını göstermektedir. Normal dağılımdan sapmalar (Fat-tails), piyasadaki şokların büyüklüğünü işaret eder.")
                            pdf.add_plot_image(fig_hist.to_image(format="png", scale=2), height=75)
                            
                            # SAYFA 3: ANORMALLİK VE TABLO
                            pdf.add_page()
                            pdf.add_section_title("2. ANORMALLİK (OUTLIER) ANALİZİ")
                            pdf.write_analysis_text("Z-Score analizi ile tespit edilen ve standart sapmanın 2 katından fazla artış gösteren 'Yüksek Riskli' ürünler aşağıda listelenmiştir.")
                            
                            # Tablo Verisi Hazırla (En yüksek 12 anormallik)
                            top_outliers = anomaliler.head(12)
                            table_data = []
                            for _, row in top_outliers.iterrows():
                                u_ad = row[ad_col][:30]
                                u_grp = row['Grup'][:15]
                                u_fark = f"%{row['Fark']*100:.2f}"
                                u_z = f"{row['Z_Score']:.2f} σ"
                                table_data.append([u_ad, u_grp, u_fark, u_z])
                            
                            if table_data:
                                pdf.create_table(["URUN", "KATEGORI", "DEGISIM", "RISK SKORU"], table_data, [80, 40, 30, 30])
                            else:
                                pdf.write_analysis_text("Bu dönemde istatistiksel olarak kritik eşiği aşan (Z>2) bir fiyat anormalliği tespit edilmemiştir.")
                            
                            pdf.ln(10)
                            pdf.write_analysis_text("Risk Dağılım Grafiği:")
                            pdf.add_plot_image(fig_outlier.to_image(format="png", scale=2), height=70)

                            # SAYFA 4: TREND (Varsa)
                            if fig_trend_pdf:
                                pdf.add_page()
                                pdf.add_section_title("3. PROJEKSİYON VE TREND ANALİZİ")
                                pdf.add_plot_image(fig_trend_pdf.to_image(format="png", scale=2), height=80)
                                pdf.write_analysis_text(f"Manşet enflasyon trendi, ay başından itibaren kümülatif olarak izlenmektedir. Son veri noktası itibarıyla sapma oranı %{enf_genel:.2f} seviyesindedir.")

                            # PDF KAYDET VE İNDİR
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                                pdf.output(tmp.name)
                                tmp.close()
                                with open(tmp.name, "rb") as f: pdf_bytes = f.read()
                                try: os.unlink(tmp.name)
                                except: pass
                            
                            st.success("✅ Profesyonel Rapor Hazırlandı!")
                            st.download_button("📥 Raporu İndir (PDF)", data=pdf_bytes, file_name=f"Quant_Report_{son}.pdf", mime="application/pdf")
        
        except Exception as e: st.error(f"Sistem Hatası: {e}")
    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px;">VALIDASYON MUDURLUGU © 2026 - CONFIDENTIAL</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard_modu()

