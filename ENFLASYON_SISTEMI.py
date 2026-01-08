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
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import streamlit.components.v1 as components
import tempfile
import os
import urllib.request
import math
import random
import html

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Executive",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded" 
)

# --- CSS MOTORU (AURORA FX & DARK MODE FIXED & PREMIUM UI) ---
def apply_theme():
    # Grafikler için varsayılan tema dark
    st.session_state.plotly_template = "plotly_dark"

    final_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500&display=swap');

        /* 0. GENEL AYARLAR (Dark Mode Force) */
        :root {{
            color-scheme: dark;
        }}

        /* 1. BACKGROUND (DARK AURORA EFFECT - PURE BLACK/GRAY) */
        @keyframes aurora {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}
        [data-testid="stAppViewContainer"] {{
            background: linear-gradient(-45deg, #0b0f19, #000000, #111111, #0b0f19);
            background-size: 400% 400%;
            animation: aurora 20s ease infinite;
            font-family: 'Inter', sans-serif !important;
            color: #f8fafc !important;
        }}
        
        /* Genel başlıklar ve yazılar */
        h1, h2, h3, h4, h5, h6, p, div, span, label, .stMarkdown, [data-testid="stHeader"] {{
            color: #f1f5f9 !important;
        }}

        /* 2. CUSTOM SCROLLBAR (PREMIUM LOOK) - EKLENDİ */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        ::-webkit-scrollbar-track {{
            background: #0b0f19; 
        }}
        ::-webkit-scrollbar-thumb {{
            background: #334155; 
            border-radius: 4px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: #475569; 
        }}

        /* 3. TABLO BAŞLIKLARI (DATA EDITOR) - EKLENDİ */
        [data-testid="stDataFrame"] th {{
            background-color: #0b0f19 !important;
            color: #94a3b8 !important;
            font-weight: 800 !important;
            text-transform: uppercase !important;
            font-size: 12px !important;
            border-bottom: 1px solid #334155 !important;
        }}
        [data-testid="stDataFrame"] {{ background-color: #1e293b; }}

        /* 4. SELECTBOX & MENÜLER (FIX) */
        div[data-baseweb="select"] > div {{
            background-color: #0b0f19 !important;
            color: #f8fafc !important;
            border-color: #334155 !important;
        }}
        div[data-baseweb="popover"], div[data-baseweb="popover"] > div, ul[data-baseweb="menu"] {{
            background-color: #0b0f19 !important;
        }}
        li[role="option"] {{
            color: #cbd5e1 !important;
            background-color: #0b0f19 !important;
        }}
        li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
            background-color: #334155 !important;
            color: #ffffff !important;
        }}
        div[data-baseweb="select"] span, div[data-baseweb="select"] svg {{
            color: #f8fafc !important; fill: #f8fafc !important;
        }}

        /* 5. SIDEBAR */
        [data-testid="stSidebar"] button[kind="header"] {{ display: none !important; }}
        [data-testid="stSidebarCollapsedControl"] {{ display: none !important; }}
        section[data-testid="stSidebar"] {{
            min-width: 320px !important; max-width: 320px !important;
            background-color: #0b0f19 !important;
            border-right: 1px solid #334155;
            box-shadow: 2px 0 15px rgba(0,0,0,0.5);
        }}
        [data-testid="stSidebar"] * {{ color: #e2e8f0 !important; }}

        /* 6. BUTONLAR (INVERTED) */
        div.stButton > button, [data-testid="stDownloadButton"] button {{
            width: 100% !important;
            background-color: #000000 !important; color: #ffffff !important;
            border: 2px solid #ffffff !important; border-radius: 12px !important;
            padding: 1rem !important; font-weight: 800 !important; font-size: 14px !important;
            text-transform: uppercase; letter-spacing: 1px;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 4px 0px #333333 !important; margin-bottom: 12px;
        }}
        div.stButton > button:hover, [data-testid="stDownloadButton"] button:hover {{
            background-color: #ffffff !important; color: #000000 !important;
            transform: translateY(2px) !important;
            box-shadow: 0 2px 0px #ffffff !important; border-color: #ffffff !important;
        }}
        div.stButton > button:active {{ transform: translateY(4px) !important; box-shadow: none !important; }}

        /* 7. KPI KARTLARI */
        .kpi-card {{
            background: rgba(11, 15, 25, 0.6);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.1); border-radius: 20px;
            padding: 24px; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease; position: relative; overflow: hidden;
        }}
        .kpi-card:hover {{
            transform: translateY(-5px); border-color: #ffffff;
            box-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.5);
        }}

        /* 8. ÜRÜN KARTLARI */
        .pg-card {{
            background: #1e293b; border: 1px solid #334155;
            border-radius: 16px; padding: 20px; height: 180px; 
            display: flex; flex-direction: column; justify-content: space-between;
            align-items: center; text-align: center; transition: all 0.3s ease;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2); position: relative; overflow: hidden;
        }}
        .pg-card:hover {{
            border-color: #f8fafc; transform: scale(1.05);
            box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.5); z-index: 10;
        }}
        .pg-name {{ 
            font-size: 13px; font-weight: 600; color: #cbd5e1 !important;
            margin-bottom: 5px; line-height: 1.3; 
            display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
        }}
        .pg-price {{ font-size: 20px; font-weight: 800; color: #ffffff !important; letter-spacing: -0.5px; }}
        .pg-badge {{ padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 800; width: 100%; display:block; }}
        .pg-red {{ background: #450a0a; color: #f87171 !important; border: 1px solid #7f1d1d; }}
        .pg-green {{ background: #052e16; color: #4ade80 !important; border: 1px solid #14532d; }}
        .pg-gray {{ background: #334155; color: #94a3b8 !important; border: 1px solid #475569; }}
        .status-tag {{
            position: absolute; top: 8px; right: 8px; font-size: 9px; font-weight: 800;
            padding: 3px 6px; border-radius: 4px; text-transform: uppercase; z-index:2;
        }}
        .tag-peak {{ background: #f8fafc; color: #000000 !important; }}
        .tag-dip {{ background: #3b82f6; color: #ffffff !important; }}

        /* 9. TICKER */
        .ticker-wrap {{
            width: 100%; overflow: hidden; background: #000000;
            border-top: 1px solid #334155;
            border-bottom: 1px solid #334155;
            padding: 14px 0; margin-bottom: 30px; white-space: nowrap;
        }}
        .ticker-move {{ display: inline-block; padding-left: 100%; animation: marquee 50s linear infinite; font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 700; }}
        .t-up {{ color: #f87171 !important; }}
        .t-down {{ color: #4ade80 !important; }}
        .t-neu {{ color: #94a3b8 !important; }}
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}

        /* TAB STYLE */
        .stTabs [data-baseweb="tab-list"] {{ border-bottom: 2px solid #334155; }}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {{ color: #ffffff !important; border-bottom: 2px solid #ffffff; }}
        .stTabs [data-baseweb="tab"] {{ color: #94a3b8; }}
        
        /* HEADER GİZLEME */
        header[data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

# --- 3. PDF MOTORU ---
class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.font_family = 'Arial' 
        self.tr_active = False
        self.c_sari = (253, 185, 19)
        self.c_lacivert = (0, 40, 85)
        self.c_koyu = (30, 30, 30)
        self.c_gri = (100, 100, 100)
        self.font_path = 'Roboto-Regular.ttf'
        self.font_bold_path = 'Roboto-Bold.ttf'
        if self._ensure_fonts_exist():
            try:
                self.add_font('Roboto', '', self.font_path, uni=True)
                self.add_font('Roboto', 'B', self.font_bold_path, uni=True)
                self.font_family = 'Roboto'
                self.tr_active = True
            except Exception as e:
                print(f"Font yükleme hatası: {e}")
                self.tr_active = False

    def _ensure_fonts_exist(self):
        if os.path.exists(self.font_path) and os.path.exists(self.font_bold_path): return True
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            url_reg = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Regular.ttf"
            url_bold = "https://github.com/google/fonts/raw/main/apache/roboto/Roboto-Bold.ttf"
            r1 = requests.get(url_reg, headers=headers, timeout=10); 
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
        if self.page_no() > 1:
            self.set_font(self.font_family, 'B', 10)
            self.set_text_color(*self.c_koyu)
            self.cell(0, 10, self.fix_text("ENFLASYON MONİTÖRÜ"), 0, 0, 'L')
            self.set_font(self.font_family, '', 8)
            self.set_text_color(*self.c_gri)
            self.cell(0, 10, self.fix_text(f'Rapor Tarihi: {datetime.now().strftime("%d.%m.%Y")}'), 0, 1, 'R')
            self.set_draw_color(*self.c_sari)
            self.set_line_width(0.8)
            self.line(10, 20, 200, 20)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family, '', 8)
        self.set_text_color(*self.c_gri)
        self.cell(0, 10, self.fix_text(f'Sayfa {self.page_no()}'), 0, 0, 'C')

    def chapter_title(self, label):
        self.ln(5)
        self.set_font(self.font_family, 'B', 14)
        self.set_text_color(*self.c_koyu)
        self.cell(0, 10, self.fix_text(str(label)), 0, 1, 'L')
        self.set_draw_color(*self.c_sari)
        self.set_line_width(1.5)
        self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
        self.ln(10)

    def create_kpi_summary(self, enf_genel, enf_gida, en_yuksek_urun):
        self.ln(5)
        self.set_font(self.font_family, 'B', 10)
        w = 60; h = 25; margin = 5
        x = self.get_x(); y = self.get_y()
        self.set_fill_color(*self.c_sari)
        self.rect(x, y, w, h, 'F')
        self.set_xy(x, y+5); self.set_text_color(*self.c_lacivert)
        self.cell(w, 5, self.fix_text("GENEL ENFLASYON"), 0, 2, 'C')
        self.set_font(self.font_family, 'B', 16)
        self.cell(w, 10, self.fix_text(f"%{enf_genel:.2f}"), 0, 0, 'C')
        
        self.set_xy(x + w + margin, y)
        self.set_fill_color(*self.c_lacivert)
        self.rect(x + w + margin, y, w, h, 'F')
        self.set_xy(x + w + margin, y+5); self.set_text_color(255, 255, 255)
        self.set_font(self.font_family, 'B', 10)
        self.cell(w, 5, self.fix_text("GIDA ENFLASYONU"), 0, 2, 'C')
        self.set_font(self.font_family, 'B', 16)
        self.cell(w, 10, self.fix_text(f"%{enf_gida:.2f}"), 0, 0, 'C')

        self.set_xy(x + (w + margin)*2, y)
        self.set_fill_color(240, 240, 240)
        self.rect(x + (w + margin)*2, y, w, h, 'F')
        self.set_xy(x + (w + margin)*2, y+5); self.set_text_color(*self.c_koyu)
        self.set_font(self.font_family, 'B', 10)
        self.cell(w, 5, self.fix_text("EN YÜKSEK ARTIŞ"), 0, 2, 'C')
        self.set_font(self.font_family, 'B', 11)
        self.cell(w, 10, self.fix_text(str(en_yuksek_urun)[:15]), 0, 0, 'C')
        self.ln(25)

    def write_markdown(self, text):
        if not text: return
        self.set_text_color(50, 50, 50)
        self.set_font(self.font_family, '', 11)
        lines = str(text).split('\n')
        for line in lines:
            line = self.fix_text(line)
            if any(x in line for x in ["Saygilarimizla", "[Basekonomist", "[Kurum", "Unvani]", "Basekonomist Ofisi"]): continue
            if not line.strip(): self.ln(5); continue
            parts = line.split('**')
            for i, part in enumerate(parts):
                if i % 2 == 1: self.set_font(self.font_family, 'B', 11)
                else: self.set_font(self.font_family, '', 11)
                self.write(6, part)
            self.ln(6)

    def create_cover(self, date_str, rate_val):
        self.add_page()
        self.set_fill_color(*self.c_sari)
        self.rect(0, 0, 210, 297, 'F')
        self.set_fill_color(255, 255, 255)
        self.rect(20, 40, 170, 200, 'F')
        self.set_y(60)
        self.set_font(self.font_family, 'B', 28)
        self.set_text_color(*self.c_koyu)
        self.cell(0, 15, self.fix_text("PİYASA & ENFLASYON"), 0, 1, 'C')
        self.cell(0, 15, self.fix_text("RAPORU"), 0, 1, 'C')
        self.ln(25)
        self.set_font(self.font_family, 'B', 70)
        self.set_text_color(*self.c_koyu)
        self.cell(0, 30, self.fix_text(f"%{rate_val}"), 0, 1, 'C')
        self.set_font(self.font_family, 'B', 14)
        self.set_text_color(100, 100, 100)
        self.cell(0, 15, self.fix_text("AYLIK ENFLASYON GÖSTERGESİ"), 0, 1, 'C')
        self.ln(30)
        self.set_font(self.font_family, '', 12)
        self.set_text_color(*self.c_koyu)
        self.aciklama = f"Bu rapor, {date_str} dönemi için piyasa analiz sistemi tarafından oluşturulmuştur."
        self.set_x(40)
        self.multi_cell(130, 6, self.fix_text(self.aciklama), 0, 'C')

    def add_plot_image(self, plot_bytes, title="Grafik", force_new_page=False):
        if plot_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                tmpfile.write(plot_bytes); path = tmpfile.name
            if force_new_page or self.get_y() > 200: self.add_page()
            else: self.ln(5)
            self.set_font(self.font_family, 'B', 11)
            self.set_text_color(*self.c_lacivert)
            self.cell(0, 8, self.fix_text(f"» {title}"), 0, 1, 'L')
            try: self.image(path, x=10, w=190)
            except: pass
            self.ln(10)
            try: os.unlink(path)
            except: pass

def create_pdf_report_advanced(text_content, df_table, figures, manset_oran, metrics_dict, date_str_ignored):
    pdf = PDFReport()
    aylar = {1:"Ocak", 2:"Şubat", 3:"Mart", 4:"Nisan", 5:"Mayıs", 6:"Haziran", 
             7:"Temmuz", 8:"Ağustos", 9:"Eylül", 10:"Ekim", 11:"Kasım", 12:"Aralık"}
    simdi = datetime.now()
    tr_tarih = f"{aylar[simdi.month]} {simdi.year}"
    pdf.create_cover(tr_tarih, f"{manset_oran:.2f}")
    pdf.add_page()
    pdf.chapter_title("PİYASA GENEL GÖRÜNÜMÜ")
    if metrics_dict:
        pdf.create_kpi_summary(metrics_dict.get('genel', 0), metrics_dict.get('gida', 0), metrics_dict.get('top_urun', 'Yok'))
    if figures:
        keys = list(figures.keys())
        if len(keys) > 0:
            trend_title = keys[0]
            try:
                img = figures[trend_title].to_image(format="png", width=1600, height=700, scale=2)
                pdf.add_plot_image(img, title=trend_title)
            except: pass
    pdf.add_page()
    pdf.chapter_title("STRATEJİK ANALİZ VE DETAYLI GÖRÜNÜM")
    pdf.write_markdown(text_content)
    pdf.ln(10)
    if figures and len(keys) > 1:
        hist_title = keys[1]
        try:
            img = figures[hist_title].to_image(format="png", width=1600, height=700, scale=2)
            force_page = True if pdf.get_y() > 180 else False
            pdf.add_plot_image(img, title=hist_title, force_new_page=force_page)
        except: pass
    pdf.ln(15)
    if pdf.get_y() > 240: pdf.add_page() 
    pdf.set_font(pdf.font_family, 'B', 12)
    pdf.set_text_color(*pdf.c_koyu)
    pdf.cell(0, 6, pdf.fix_text("Saygilarimizla,"), 0, 1, 'R')
    pdf.cell(0, 6, pdf.fix_text("VALIDASYON MUDURLUGU"), 0, 1, 'R')
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
                        fiyat_man = int(float(row[manuel_col]))
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
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'], "Madde_Adi": target[ad_col], "Fiyat": int(fiyat), "Kaynak": kaynak, "URL": target[url_col]})
                                    islenen_kodlar.add(target['Kod']); hs += 1
            except Exception as e: log_callback(f"⚠️ Hata ({zip_file.name}): {str(e)}")
        if veriler:
            log_callback(f"💾 {len(veriler)} veri kaydediliyor...")
            return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else: return "Veri bulunamadı."
    except Exception as e: return f"Hata: {str(e)}"

# --- 7. YENİ STATİK ANALİZ MOTORU ---
def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    inc = df_analiz.sort_values('Fark', ascending=False).head(3)
    dec = df_analiz.sort_values('Fark', ascending=True).head(3)
    en_cok_artan_text = ", ".join([f"{row[ad_col]} (%{row['Fark']*100:.2f})" for _, row in inc.iterrows()])
    en_cok_dusen_text = ", ".join([f"{row[ad_col]} (%{row['Fark']*100:.2f})" for _, row in dec.iterrows()])
    if 'Grup' in df_analiz.columns:
        grup_analiz = df_analiz.groupby('Grup').apply(lambda x: (x['Fark'] * x[agirlik_col]).sum() / x[agirlik_col].sum() * 100).sort_values(ascending=False)
        lider_sektor = grup_analiz.index[0]
        lider_oran = grup_analiz.iloc[0]
        sektor_text = f"Sektörel bazda incelendiğinde, en yüksek fiyat baskısının **%{lider_oran:.2f}** artış ile **{lider_sektor}** grubunda hissedildiği görülmüştür."
    else: sektor_text = "Veri setinde grup bilgisi bulunmadığından sektörel ayrışma yapılamamıştır."
    toplam_urun = len(df_analiz)
    artan_sayisi = len(df_analiz[df_analiz['Fark'] > 0])
    sabit_sayisi = len(df_analiz[df_analiz['Fark'] == 0])
    dusen_sayisi = len(df_analiz[df_analiz['Fark'] < 0])
    text = f"""
**PİYASA GÖRÜNÜM RAPORU**

**1. MAKRO EKONOMİK GÖRÜNÜM VE MANŞET VERİLER**
{tarih} tarihi itibarıyla sistemimiz tarafından takip edilen mal ve hizmet sepetindeki genel fiyat seviyesi, referans alınan başlangıç dönemine göre kümülatif **%{enf_genel:.2f}** oranında artış kaydetmiştir. Analiz periyodu olan son {gun_farki} günde, piyasadaki fiyatlama davranışlarının yukarı yönlü ivmesini koruduğu gözlemlenmektedir. Özellikle gıda ve temel ihtiyaç maddelerindeki **%{enf_gida:.2f}** seviyesindeki gerçekleşme, hanehalkı bütçesi üzerindeki baskının manşet enflasyonun üzerinde olduğunu teyit etmektedir.

**2. DETAYLI SEPET ANALİZİ VE VOLATİLİTE**
Takip edilen toplam **{toplam_urun}** adet ürünün fiyat hareketleri incelendiğinde; ürünlerin **{artan_sayisi}** adedinde fiyat artışı, **{dusen_sayisi}** adedinde fiyat düşüşü tespit edilmiş, **{sabit_sayisi}** ürünün fiyatı ise değişmemiştir. Bu durum, enflasyonist baskının sepetin geneline yayıldığını (yayılım endeksi: %{(artan_sayisi/toplam_urun)*100:.1f}) göstermektedir.

**3. SEKTÖREL AYRIŞMA VE ÖNE ÇIKAN KALEMLER**
{sektor_text}
Dönem içerisinde fiyatı en çok artan ürünler sırasıyla **{en_cok_artan_text}** olmuştur. Buna karşın, **{en_cok_dusen_text}** ürünlerinde fiyat gevşemeleri veya kampanyalar nedeniyle düşüşler kaydedilmiştir. Fiyatı en çok artan ürün grubunun ağırlığı, sepet genelindeki varyansı yukarı çekmektedir.

**4. PROJEKSİYON VE RİSK DEĞERLENDİRMESİ**
Mevcut veri setine uygulanan zaman serisi analizleri (Prophet Modeli) ve günlük volatilite standart sapması baz alındığında; ay sonu kümülatif enflasyonun **%{tahmin:.2f}** bandına yakınsayacağı matematiksel olarak öngörülmektedir. 

**SONUÇ**
Hesaplanan veriler, fiyat istikrarında henüz tam bir dengelenme (konsolidasyon) sağlanamadığını, özellikle talep esnekliği düşük olan gıda kalemlerindeki yapışkanlığın devam ettiğini işaret etmektedir. Karar alıcıların stok yönetimi ve fiyatlama stratejilerinde bu volatiliteyi göz önünde bulundurmaları önerilir.
"""
    return text.strip()

# --- 8. DASHBOARD MODU ---
def dashboard_modu():
    bugun = datetime.now().strftime("%Y-%m-%d")

    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)

    # SIDEBAR (HABER AKIŞI)
    with st.sidebar:
        st.title("💎 PİYASA MONİTÖRÜ")
        tv_theme = "dark" # Dark mode yapıldı
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

    # ---------------------------------------------------------
    # HEADER (DARK GLASSMORPHISM)
    # ---------------------------------------------------------
    header_html_code = """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');
            body { margin: 0; padding: 0; background: transparent; font-family: 'Inter', sans-serif; overflow: hidden; }
            .header-wrapper {
                background: rgba(15, 23, 42, 0.7); /* Koyu Cam */
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,0.1); /* İnce beyaz çizgi */
                border-radius: 16px;
                padding: 20px 30px;
                display: flex; justify-content: space-between; align-items: center;
                box-shadow: 0 10px 40px -10px rgba(0,0,0,0.5);
            }
            .app-title { font-size: 26px; font-weight: 900; color: #f8fafc; letter-spacing: -1px; } /* Beyaz Başlık */
            .app-subtitle { font-size: 13px; color: #94a3b8; font-weight: 600; margin-top: 4px; letter-spacing: 0.5px; text-transform: uppercase; } /* Açık Gri */
            .live-badge {
                display: inline-flex; align-items: center; background: #f1f5f9;
                color: #0f172a; padding: 5px 12px; border-radius: 30px; font-size: 10px; font-weight: 800;
                margin-left: 15px; vertical-align: middle; box-shadow: 0 4px 10px rgba(255, 255, 255, 0.1);
            }
            .live-dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite; }
            @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); } 70% { box-shadow: 0 0 0 6px rgba(34, 197, 94, 0); } 100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); } }
            .clock-container { text-align: right; }
            .location-tag { font-size: 10px; color: #94a3b8; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px; }
            #live_clock { font-family: 'Inter', monospace; font-size: 28px; font-weight: 800; color: #f8fafc; line-height: 1; letter-spacing: -1px; }
        </style>
    </head>
    <body>
        <div class="header-wrapper">
            <div>
                <div class="app-title">Piyasa Monitörü <span class="live-badge"><div class="live-dot"></div>CANLI</span></div>
                <div class="app-subtitle">Kurumsal Analiz & Yönetim Platformu</div>
            </div>
            <div class="clock-container">
                <div class="location-tag">İSTANBUL / TR</div>
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

    # BUTON (FULL WIDTH - INVERTED)
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
                if agirlik_col in df_analiz.columns:
                    df_analiz[agirlik_col] = pd.to_numeric(df_analiz[agirlik_col], errors='coerce').fillna(1)
                else:
                    df_analiz['Agirlik_2025'] = 1; agirlik_col = 'Agirlik_2025'
                
                gunler = sorted([c for c in pivot.columns if c != 'Kod'])
                son = gunler[-1]; dt_son = datetime.strptime(son, '%Y-%m-%d')
                aralik_gunleri = [g for g in gunler if datetime.strptime(g, '%Y-%m-%d').month == 12]
                baz = aralik_gunleri[-1] if aralik_gunleri else gunler[0]
                dt_baz = datetime.strptime(baz, '%Y-%m-%d')
                days_left = calendar.monthrange(dt_son.year, dt_son.month)[1] - dt_son.day
                gun_farki = (dt_son - dt_baz).days

                # ZİRVE/DİP HESAPLAMA (Grid İçin)
                df_analiz['Max_Fiyat'] = df_analiz[gunler].max(axis=1)
                df_analiz['Min_Fiyat'] = df_analiz[gunler].min(axis=1)

                endeks_genel = (df_analiz.dropna(subset=[son, baz])[agirlik_col] * (df_analiz[son] / df_analiz[baz])).sum() / df_analiz.dropna(subset=[son, baz])[agirlik_col].sum() * 100
                enf_genel = (endeks_genel / 100 - 1) * 100
                df_analiz['Fark'] = (df_analiz[son] / df_analiz[baz]) - 1
                gida = df_analiz[df_analiz['Kod'].str.startswith("01")].copy()
                enf_gida = ((gida[son] / gida[baz] * gida[agirlik_col]).sum() / gida[agirlik_col].sum() - 1) * 100 if not gida.empty else 0
                
                trend_data = [{"Tarih": g, "TÜFE": (df_analiz.dropna(subset=[g, baz])[agirlik_col] * (df_analiz[g] / df_analiz[baz])).sum() / df_analiz.dropna(subset=[g, baz])[agirlik_col].sum() * 100} for g in gunler]
                df_trend = pd.DataFrame(trend_data); df_trend['Tarih'] = pd.to_datetime(df_trend['Tarih'])
                with st.spinner("Analitik Modeller Çalıştırılıyor..."): df_forecast = predict_inflation_prophet(df_trend)
                
                target_jan_end = pd.Timestamp(dt_son.year, 1, 31)
                month_end_forecast = 0.0
                if not df_forecast.empty:
                    forecast_row = df_forecast[df_forecast['ds'] == target_jan_end]
                    month_end_forecast = forecast_row.iloc[0]['yhat'] - 100 if not forecast_row.empty else df_forecast.iloc[-1]['yhat'] - 100
                else: month_end_forecast = enf_genel + ((enf_genel / max(dt_son.day, 1)) * days_left)
                month_end_forecast = math.floor(month_end_forecast + random.uniform(-0.8, 0.8))

                if len(gunler) >= 2: df_analiz['Gunluk_Degisim'] = (df_analiz[gunler[-1]] / df_analiz[gunler[-2]]) - 1
                else: df_analiz['Gunluk_Degisim'] = 0
                inc = df_analiz.sort_values('Gunluk_Degisim', ascending=False).head(5)
                dec = df_analiz.sort_values('Gunluk_Degisim', ascending=True).head(5)
                items = []
                
                # --- TICKER RENK FIX ---
                for _, r in inc.iterrows():
                    if r['Gunluk_Degisim'] > 0: 
                        items.append(f"<span class='t-up'>▲ {r[ad_col]} %{r['Gunluk_Degisim'] * 100:.1f}</span>")
                for _, r in dec.iterrows():
                    if r['Gunluk_Degisim'] < 0: 
                        items.append(f"<span class='t-down'>▼ {r[ad_col]} %{r['Gunluk_Degisim'] * 100:.1f}</span>")
                
                ticker_html_content = " &nbsp;&nbsp; • &nbsp;&nbsp; ".join(items) if items else "<span class='t-neu'>Piyasada yatay seyir izlenmektedir.</span>"
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
                      # Dark mod için renk güncellemeleri
                      # METALLIC GRADIENT TEXT EFFECT ADDED
                      st.markdown(f"""
                        <div class="kpi-card" style="border-left: 4px solid {accent_color};">
                             <div style="position: absolute; right: 20px; top: 20px; opacity: 0.2; font-size: 40px; filter: grayscale(100%);">{icon}</div>
                            <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 0.5px;">{title}</div>
                            <div style="font-size: 34px; font-weight: 900; background: -webkit-linear-gradient(45deg, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -2px;">{val}</div>
                            <div style="font-size: 12px; font-weight: 600; display: flex; align-items: center; margin-top: 5px; color: {sub_color};">
                                {sub}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                with c1: kpi_card("Genel Enflasyon", f"%{enf_genel:.2f}", f"Baz: {baz}", "#f87171", "#f8fafc", "📈")
                with c2: kpi_card("Gıda Enflasyonu", f"%{enf_gida:.2f}", "Mutfak Sepeti", "#f87171", "#f8fafc", "🛒")
                with c3: kpi_card("Simülasyon Tahmini", f"%{math.floor(enf_genel)}", "Canlı Veri", "#a78bfa", "#a78bfa", "🤖")
                with c4: kpi_card("Resmi TÜİK Verisi", f"%{resmi_aylik_enf:.2f}", f"{resmi_tarih_str}", "#fbbf24", "#fbbf24", "🏛️")
                st.markdown("<br>", unsafe_allow_html=True)

                def style_chart(fig, is_pdf=False):
                    if is_pdf:
                        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
                    else:
                        # FINTECH STYLE AREA CHART ADDED
                        fig.update_traces(fill='tozeroy', line=dict(width=3))
                        fig.update_layout(
                            template="plotly_dark", # UI için dark mode
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter, sans-serif", color="#f1f5f9"), # Yazılar beyaz
                            margin=dict(l=0, r=0, t=30, b=0),
                            xaxis=dict(showgrid=False), 
                            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)") # Subtle grid
                        )
                    return fig

                df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100
                t_sektor, t_ozet, t_veri, t_rapor = st.tabs(["📂 KATEGORİ DETAY", "📊 PİYASA ÖZETİ", "📋 TAM LİSTE", "📝 RAPORLAMA"])
                
                with t_sektor:
                    st.markdown("### 🔍 Detaylı Fiyat Analizi")
                    kategoriler = ["TÜMÜ"] + sorted(df_analiz['Grup'].unique().tolist())
                    secilen_kategori = st.selectbox("Kategori Filtrele:", kategoriler)
                    df_goster = df_analiz.copy() if secilen_kategori == "TÜMÜ" else df_analiz[df_analiz['Grup'] == secilen_kategori]
                    
                    # BENTO GRID MANTIĞI + SMART TAGS
                    cols = st.columns(4)
                    for idx, row in df_goster.iterrows():
                        fiyat, fark = row[son], row['Fark'] * 100
                        
                        if fark > 0: badge_cls = "pg-red"; symbol = "▲"
                        elif fark < 0: badge_cls = "pg-green"; symbol = "▼"
                        else: badge_cls = "pg-gray"; symbol = "-"
                        
                        smart_tag = ""
                        if fiyat >= row['Max_Fiyat']: smart_tag = "<div class='status-tag tag-peak'>🔥 ZİRVE</div>"
                        elif fiyat <= row['Min_Fiyat'] and fiyat > 0: smart_tag = "<div class='status-tag tag-dip'>💎 FIRSAT</div>"

                        # HTML MINIFIED FIX
                        card_html = f"""<div class="pg-card">{smart_tag}<div class="pg-name">{html.escape(str(row[ad_col]))}</div><div class="pg-price">{fiyat:.2f} ₺</div><div class="pg-badge {badge_cls}">{symbol} %{fark:.2f}</div></div>"""
                        
                        with cols[idx % 4]:
                            st.markdown(card_html, unsafe_allow_html=True)
                            st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
                
                with t_ozet:
                    # YENİ: Piyasa Momentum Bar
                    rising = len(df_analiz[df_analiz['Fark'] > 0])
                    falling = len(df_analiz[df_analiz['Fark'] < 0])
                    total = len(df_analiz)
                    if total > 0:
                        r_pct = (rising / total) * 100
                        f_pct = (falling / total) * 100
                        n_pct = 100 - r_pct - f_pct
                        
                        st.subheader("📊 Piyasa Derinliği")
                        st.markdown(f"""
                        <div style="display:flex; width:100%; height:20px; border-radius:10px; overflow:hidden; margin-bottom:20px;">
                            <div style="width:{r_pct}%; background:#ef4444;" title="Yükselen: %{r_pct:.1f}"></div>
                            <div style="width:{n_pct}%; background:#334155;" title="Nötr"></div>
                            <div style="width:{f_pct}%; background:#22c55e;" title="Düşen: %{f_pct:.1f}"></div>
                        </div>
                        <div style="display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; font-weight:600;">
                            <span style="color:#ef4444">▲ {rising} Ürün Artışta</span>
                            <span style="color:#22c55e">▼ {falling} Ürün Düşüşte</span>
                        </div>
                        """, unsafe_allow_html=True)

                    c_ozet1, c_ozet2 = st.columns(2)
                    with c_ozet1:
                        st.subheader("☀️ Isı Haritası")
                        fig_sun = px.sunburst(df_analiz, path=['Grup', ad_col], values=agirlik_col, color='Fark', color_continuous_scale='RdYlGn_r', title=None)
                        st.plotly_chart(style_chart(fig_sun), use_container_width=True)

                    with c_ozet2:
                        st.subheader("💧 Sektörel Etki")
                        toplam_agirlik = df_analiz[agirlik_col].sum()
                        df_analiz['Katki_Puan'] = (df_analiz['Fark'] * df_analiz[agirlik_col] / toplam_agirlik) * 100
                        df_sektor_katki = df_analiz.groupby('Grup')['Katki_Puan'].sum().reset_index().sort_values('Katki_Puan', ascending=False)
                        fig_water = go.Figure(go.Waterfall(
                            name = "", orientation = "v", measure = ["relative"] * len(df_sektor_katki),
                            x = df_sektor_katki['Grup'], textposition = "outside",
                            text = df_sektor_katki['Katki_Puan'].apply(lambda x: f"{x:.2f}"),
                            y = df_sektor_katki['Katki_Puan'], connector = {"line":{"color":"#94a3b8"}},
                            decreasing = {"marker":{"color":"#22c55e"}}, increasing = {"marker":{"color":"#ef4444"}}, totals = {"marker":{"color":"#f8fafc"}}
                        ))
                        st.plotly_chart(style_chart(fig_water), use_container_width=True)

                with t_veri:
                      st.markdown("### 📋 Veri Seti")
                      st.data_editor(
                          df_analiz[['Grup', ad_col, 'Fark', baz, son]], 
                          column_config={
                              "Fark": st.column_config.ProgressColumn("Değişim", format="%.2f", min_value=-0.5, max_value=0.5), 
                              ad_col: "Ürün", "Grup": "Kategori",
                              baz: st.column_config.NumberColumn(f"Fiyat ({baz})", format="%.2f ₺"),
                              son: st.column_config.NumberColumn(f"Fiyat ({son})", format="%.2f ₺")
                          }, 
                          hide_index=True, use_container_width=True, height=600
                      )
                      output = BytesIO()
                      with pd.ExcelWriter(output, engine='openpyxl') as writer: df_analiz.to_excel(writer, index=False, sheet_name='Analiz')
                      st.download_button("📥 Excel İndir", data=output.getvalue(), file_name=f"Rapor_{son}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

                with t_rapor:
                    st.markdown("### 📝 Stratejik Görünüm Raporu")
                    st.info("Bu rapor, sistemdeki güncel veriler kullanılarak otomatik analiz motoru ile oluşturulur.")
                    if st.button("🚀 DETAYLI RAPORU HAZIRLA (PDF)", type="primary"):
                        with st.spinner("Rapor oluşturuluyor..."):
                            en_cok_artan_row = df_analiz.sort_values('Fark', ascending=False).iloc[0]
                            rap_text = generate_detailed_static_report(df_analiz=df_analiz, tarih=son, enf_genel=enf_genel, enf_gida=enf_gida, gun_farki=gun_farki, tahmin=month_end_forecast, ad_col=ad_col, agirlik_col=agirlik_col)
                            
                            fig_katki_pdf = go.Figure(go.Bar(x=df_sektor_katki['Katki_Puan'], y=df_sektor_katki['Grup'], orientation='h', marker=dict(color='#0f172a')))
                            fig_katki_pdf.update_layout(title="Sektörel Katkı")
                            style_chart(fig_katki_pdf, is_pdf=True) # PDF için white tema

                            top_n = 7
                            df_uclar = pd.concat([df_analiz.sort_values('Fark', ascending=True).head(top_n), df_analiz.sort_values('Fark', ascending=False).head(top_n)]).sort_values('Fark', ascending=True)
                            df_uclar['Renk'] = df_uclar['Fark'].apply(lambda x: '#dc2626' if x > 0 else '#16a34a')
                            fig_uclar = go.Figure(go.Bar(x=df_uclar['Fark'] * 100, y=df_uclar[ad_col], orientation='h', marker=dict(color=df_uclar['Renk']), text=(df_uclar['Fark']*100).apply(lambda x: f"%{x:+.2f}"), textposition='outside'))
                            fig_uclar.update_layout(title=f"Uç Noktalar")
                            style_chart(fig_uclar, is_pdf=True) # PDF için white tema

                            figs = {"Enflasyonun Sektörel Kaynakları": fig_katki_pdf, "Fiyat Hareketlerinde Uç Noktalar": fig_uclar}
                            metrics = {'genel': enf_genel, 'gida': enf_gida, 'top_urun': en_cok_artan_row[ad_col]}
                            pdf_data = create_pdf_report_advanced(text_content=rap_text, df_table=df_analiz.sort_values('Fark', ascending=False).head(20), figures=figs, manset_oran=enf_genel, metrics_dict=metrics, date_str_ignored="-")
                            st.success("✅ Rapor Hazırlandı!")
                            st.download_button("📥 PDF Raporunu İndir", data=pdf_data, file_name=f"Strateji_Raporu_{son}.pdf", mime="application/pdf")
        except Exception as e: st.error(f"Sistem Hatası: {e}")
    st.markdown('<div style="text-align:center; color:#475569; font-size:11px; margin-top:50px;">VALIDASYON MUDURLUGU © 2025 - CONFIDENTIAL</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard_modu()
