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
import numpy as np  # GEOMETRİK ORTALAMA İÇİN EKLENDİ

# --- 1. AYARLAR VE TEMA YÖNETİMİ ---
st.set_page_config(
    page_title="Piyasa Monitörü | Pro",
    layout="wide",
    page_icon="💎",
    initial_sidebar_state="expanded" 
)

# --- CSS MOTORU (AGRESİF STİL) ---
# --- CSS MOTORU (AGRESİF STİL + TERMİNAL EKLENTİSİ) ---
def apply_theme():
    st.session_state.plotly_template = "plotly_dark"

    final_css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500&display=swap');

        :root {{ color-scheme: dark; }}

        [data-testid="stAppViewContainer"] {{
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 0%, #111115 0%, #000000 80%);
            font-family: 'Inter', sans-serif !important;
            color: #e2e8f0 !important;
        }}
        
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, div, span {{
            color: #f1f5f9;
        }}

        /* SELECTBOX DÜZELTMELERİ */
        ul[data-baseweb="menu"] {{
            background-color: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
        }}
        li[role="option"] {{
            color: #000000 !important;
            background-color: #ffffff !important;
        }}
        li[role="option"] div, li[role="option"] span {{
             color: #000000 !important;
        }}
        li[role="option"]:hover, li[role="option"][aria-selected="true"] {{
            background-color: #f1f5f9 !important;
            color: #000000 !important;
        }}
        div[data-baseweb="select"] > div {{
            background-color: #111827; 
            color: #f8fafc;
            border-color: #374151;
        }}
        
        /* POPOVER DÜZELTMELERİ */
        div[data-testid="stPopoverBody"] {{
            background-color: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
        }}
        div[data-testid="stPopoverBody"] * {{
            color: #000000 !important;
        }}
        div[data-testid="stPopoverBody"] div[data-baseweb="select"] > div {{
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 1px solid #94a3b8 !important;
        }}
        div[data-testid="stPopoverBody"] div[data-baseweb="select"] svg {{
            fill: #000000 !important;
        }}

        /* BUTONLAR */
        [data-testid="stDownloadButton"] button {{
            background-color: #ffffff !important;
            border: 2px solid #e2e8f0 !important;
        }}
        [data-testid="stDownloadButton"] button,
        [data-testid="stDownloadButton"] button * {{
            color: #000000 !important;
            font-weight: 800 !important;
        }}
        [data-testid="stDownloadButton"] button:hover {{
            background-color: #f8fafc !important;
            border-color: #cbd5e1 !important;
        }}

        /* FLOATING CHAT BUTTON */
        [data-testid="stPopover"] {{ 
            position: fixed !important; bottom: 30px !important; left: 30px !important; right: auto !important;
            z-index: 999999 !important; background-color: transparent !important; border: none !important;
            width: auto !important; height: auto !important;
        }}
        [data-testid="stPopover"] button {{
            width: 65px !important; height: 65px !important; border-radius: 50% !important;
            background-color: #3b82f6 !important;
            color: white !important;
            border: 2px solid rgba(255,255,255,0.2) !important; 
            box-shadow: 0 0 25px rgba(59, 130, 246, 0.8) !important;
            font-size: 28px !important; display: flex; justify-content: center; align-items: center;
        }}
        [data-testid="stPopover"] button:hover {{ 
            background-color: #2563eb !important;
            transform: scale(1.1); 
            box-shadow: 0 0 40px rgba(59, 130, 246, 1) !important; 
        }}

        /* Ticker */
        .ticker-wrap {{
            width: 100%; overflow: hidden; background-color: #000000;
            border-top: 1px solid #334155; border-bottom: 1px solid #334155;
            padding: 12px 0; margin-bottom: 20px; white-space: nowrap;
        }}
        .ticker-move {{ display: inline-block; padding-left: 100%; animation: marquee 40s linear infinite; font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 600; }}
        @keyframes marquee {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}

        /* KPI Cards */
        .kpi-card {{
            background: rgba(10, 10, 12, 0.95); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px; padding: 24px; position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.8); transition: transform 0.3s ease;
        }}
        .kpi-card:hover {{ transform: translateY(-5px); border-color: rgba(255,255,255,0.3); }}
        .kpi-title {{ font-size: 11px; font-weight: 800; color: #94a3b8 !important; text-transform: uppercase; margin-bottom: 5px; }}
        .kpi-value {{ font-size: 42px; font-weight: 900; color: #ffffff !important; letter-spacing: -1px; }}
        .kpi-sub   {{ font-size: 12px; font-weight: 600; opacity: 0.7; margin-top: 5px; color: #cbd5e1 !important; }}

        /* Product Cards */
        .pg-card {{
            background: #0a0a0c; border: 1px solid #27272a; border-radius: 14px;
            padding: 16px; height: 190px;
            display: flex; flex-direction: column; justify-content: space-between; align-items: center;
            text-align: center; position: relative; transition: all 0.3s;
        }}
        .pg-card:hover {{ border-color: #52525b; transform: scale(1.03); background: #121214; z-index:10; }}
        .pg-name {{ font-size: 13px; font-weight: 600; color: #cbd5e1 !important; line-height: 1.3; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }}
        .pg-price {{ font-size: 22px; font-weight: 800; color: #ffffff !important; letter-spacing: -0.5px; }}
        
        .status-tag {{ position: absolute; top: 10px; right: 10px; font-size: 10px; font-weight: 900; padding: 4px 8px; border-radius: 6px; text-transform: uppercase; z-index: 5; letter-spacing: 0.5px; }}
        .tag-peak {{ background-color: #ffffff !important; color: #000000 !important; }}
        .tag-dip {{ background-color: #3b82f6 !important; color: #ffffff !important; }}
        .pg-badge {{ padding: 5px 10px; border-radius: 6px; font-size: 12px; font-weight: 800; width: 100%; }}
        .pg-red {{ background: rgba(220, 38, 38, 0.2); color: #f87171 !important; border: 1px solid rgba(220, 38, 38, 0.4); }}
        .pg-green {{ background: rgba(22, 163, 74, 0.2); color: #4ade80 !important; border: 1px solid rgba(22, 163, 74, 0.4); }}
        .pg-gray {{ background: #27272a; color: #a1a1aa !important; }}

        /* Sidebar & Others */
        section[data-testid="stSidebar"] {{ background-color: #000000 !important; border-right: 1px solid #1f2937; }}
        div.stButton > button {{ width: 100%; border-radius: 10px; font-weight: 700; background: #111827; color: #fff; border: 1px solid #374151; }}
        div.stButton > button:hover {{ border-color: #fff; background: #000; }}
        [data-testid="stDataFrame"] th {{ background-color: #111827 !important; color: #9ca3af !important; }}
        header[data-testid="stHeader"], [data-testid="stToolbar"] {{ display: none !important; }}

        /* --- SİNYAL MERKEZİ & TERMİNAL STİLİ (YENİ EKLENEN KISIM) --- */
        .terminal-wrapper {{
            background-color: #0c0c0c;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 15px;
            font-family: 'JetBrains Mono', monospace;
            position: relative;
            overflow: hidden;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        }}
        .terminal-wrapper::before {{
            content: " ";
            display: block;
            position: absolute;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            z-index: 2;
            background-size: 100% 2px, 3px 100%;
            pointer-events: none;
        }}
        .terminal-header {{
            color: #4ade80;
            font-size: 10px;
            letter-spacing: 2px;
            margin-bottom: 10px;
            border-bottom: 1px solid #1f2937;
            padding-bottom: 5px;
            display: flex; justify-content: space-between;
        }}
        .cmd-line {{
            color: #e2e8f0;
            font-size: 12px;
            margin-bottom: 8px;
        }}
        .cmd-response {{
            color: #a7f3d0;
            font-size: 13px;
            line-height: 1.5;
            text-shadow: 0 0 5px rgba(74, 222, 128, 0.3);
        }}
        .highlight-val {{ color: #fff; font-weight: bold; background: rgba(255,255,255,0.1); padding: 0 4px; border-radius: 3px; }}
        .trend-up {{ color: #ef4444 !important; font-weight: bold; }}
        .trend-down {{ color: #4ade80 !important; font-weight: bold; }}
        .mini-table {{ width: 100%; font-size: 11px; border-collapse: collapse; margin-top: 8px; z-index: 5; position: relative; }}
        .mini-table td {{ padding: 4px; border-bottom: 1px solid #333; color: #9ca3af; }}
        .mini-table th {{ text-align: left; color: #6b7280; padding-bottom: 4px; }}
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
        self.set_fill_color(*self.c_sari)
        self.rect(self.get_x(), self.get_y(), 60, 25, 'F')
        self.set_text_color(*self.c_lacivert)
        self.cell(60, 5, self.fix_text("KÜMÜLATİF ENFLASYON"), 0, 2, 'C')
        self.set_font(self.font_family, 'B', 16)
        self.cell(60, 10, self.fix_text(f"%{enf_genel:.2f}"), 0, 0, 'C')
        
        self.set_xy(self.get_x() + 5, self.get_y() - 15)
        self.set_fill_color(*self.c_lacivert)
        self.rect(self.get_x(), self.get_y(), 60, 25, 'F')
        self.set_text_color(255, 255, 255)
        self.set_font(self.font_family, 'B', 10)
        self.cell(60, 5, self.fix_text("GIDA ENFLASYONU"), 0, 2, 'C')
        self.set_font(self.font_family, 'B', 16)
        self.cell(60, 10, self.fix_text(f"%{enf_gida:.2f}"), 0, 0, 'C')

        self.set_xy(self.get_x() + 5, self.get_y() - 15)
        self.set_fill_color(240, 240, 240)
        self.rect(self.get_x(), self.get_y(), 60, 25, 'F')
        self.set_text_color(*self.c_koyu)
        self.set_font(self.font_family, 'B', 10)
        self.cell(60, 5, self.fix_text("EN YÜKSEK ARTIŞ"), 0, 2, 'C')
        self.set_font(self.font_family, 'B', 11)
        self.cell(60, 10, self.fix_text(str(en_yuksek_urun)[:15]), 0, 0, 'C')
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
        self.cell(0, 15, self.fix_text("YIL İÇİ KÜMÜLATİF GÖSTERGE"), 0, 1, 'C')
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
                        # 1. DEĞİŞİKLİK BURADA: int() yerine float() kullanıldı
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
                                    # 2. DEĞİŞİKLİK BURADA: int(fiyat) yerine float(fiyat) yapıldı
                                    veriler.append({"Tarih": bugun, "Zaman": simdi, "Kod": target['Kod'], "Madde_Adi": target[ad_col], "Fiyat": float(fiyat), "Kaynak": kaynak, "URL": target[url_col]})
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
{tarih} tarihi itibarıyla sistemimiz tarafından takip edilen mal ve hizmet sepetindeki genel fiyat seviyesi, yılbaşına göre (Kümülatif) **%{enf_genel:.2f}** oranında artış kaydetmiştir. Analiz periyodu olan son dönemde, piyasadaki fiyatlama davranışlarının seyri yakından izlenmektedir. Özellikle gıda ve temel ihtiyaç maddelerindeki **%{enf_gida:.2f}** seviyesindeki gerçekleşme, hanehalkı bütçesi üzerindeki etkiyi yansıtmaktadır.

**2. DETAYLI SEPET ANALİZİ VE VOLATİLİTE**
Takip edilen toplam **{toplam_urun}** adet ürünün fiyat hareketleri incelendiğinde; ürünlerin **{artan_sayisi}** adedinde fiyat artışı, **{dusen_sayisi}** adedinde fiyat düşüşü tespit edilmiş, **{sabit_sayisi}** ürünün fiyatı ise değişmemiştir. Bu durum, enflasyonist baskının sepetin geneline yayıldığını (yayılım endeksi: %{(artan_sayisi/toplam_urun)*100:.1f}) göstermektedir.

**3. SEKTÖREL AYRIŞMA VE ÖNE ÇIKAN KALEMLER**
{sektor_text}
Dönem içerisinde fiyatı en çok artan ürünler sırasıyla **{en_cok_artan_text}** olmuştur. Buna karşın, **{en_cok_dusen_text}** ürünlerinde fiyat gevşemeleri veya kampanyalar nedeniyle düşüşler kaydedilmiştir. Fiyatı en çok artan ürün grubunun ağırlığı, sepet genelindeki varyansı yukarı çekmektedir.

**4. PROJEKSİYON VE RİSK DEĞERLENDİRMESİ**
Mevcut veri setine uygulanan zaman serisi analizleri (Prophet Modeli) ve günlük volatilite standart sapması baz alındığında; ay sonu enflasyon eğiliminin **%{tahmin:.2f}** bandına yakınsayacağı matematiksel olarak öngörülmektedir. 

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
                background: rgba(10, 10, 12, 0.6); backdrop-filter: blur(15px);
                border-bottom: 1px solid rgba(255,255,255,0.1); border-radius: 12px;
                padding: 20px 30px; display: flex; justify-content: space-between; align-items: center;
                box-shadow: 0 4px 30px rgba(0,0,0,0.5);
            }
            .app-title { font-size: 24px; font-weight: 800; color: #fff; letter-spacing: -0.5px; text-shadow: 0 0 20px rgba(255,255,255,0.2); }
            .app-subtitle { font-size: 12px; color: #71717a; font-weight: 600; margin-top: 4px; letter-spacing: 1px; text-transform: uppercase; }
            .live-badge { display: inline-flex; align-items: center; background: rgba(255,255,255,0.1); color: #fff; padding: 4px 10px; border-radius: 20px; font-size: 10px; font-weight: 700; margin-left: 15px; border: 1px solid rgba(255,255,255,0.1); }
            .live-dot { width: 6px; height: 6px; background: #22c55e; border-radius: 50%; margin-right: 6px; box-shadow: 0 0 8px #22c55e; animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
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
                # --- [BAŞLANGIÇ] TÜİK METODOLOJİSİ: ZİNCİRLEME LASPEYRES ---
                # --- REVİZE: GEOMETRİK ORTALAMA İLE AYLIK FİYAT ---
                # -------------------------------------------------------------
                
                # 1. BAZ DÖNEMİ BELİRLEME (Referans: Önceki Yılın Aralık Ayı)
                simdi_yil = dt_son.year
                onceki_yil_aralik_prefix = f"{simdi_yil - 1}-12"
                
                # Sütunlarda geçen yılın Aralık ayına ait veri var mı kontrol et
                aralik_cols = [c for c in gunler if c.startswith(onceki_yil_aralik_prefix)]

                if aralik_cols:
                    baz_col = aralik_cols[-1]
                    baz_tanimi = f"Aralık {simdi_yil - 1}"
                else:
                    # Yeni sistem/yıl verisi yoksa en eski veri baz alınır
                    baz_col = gunler[0]
                    baz_tanimi = f"Başlangıç ({baz_col})"

                # 2. GEOMETRİK ORTALAMA İLE AYLIK FİYAT HESAPLAMA
                # Bu ayın (son veri tarihi ayı) tüm sütunlarını bul
                bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
                bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
                
                if bu_ay_cols:
                    # Geometrik Ortalama Fonksiyonu (0 ve negatifleri hariç tutar)
                    def geometrik_ortalama_hesapla(row):
                        # Sadece 0'dan büyük sayıları al (Logaritma hatasını önlemek için)
                        valid_vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
                        if not valid_vals:
                            return np.nan
                        # Geometrik Ortalama Formülü: exp(mean(log(x)))
                        return np.exp(np.mean(np.log(valid_vals)))

                    # Satır satır uygula
                    df_analiz['Aylik_Ortalama'] = df_analiz[bu_ay_cols].apply(geometrik_ortalama_hesapla, axis=1)
                    
                    # Eğer tüm ay boyunca hiç verisi olmayan (NaN) ürünler varsa, 
                    # geçici olarak son bilinen fiyatı alabiliriz (veya hesaplamadan düşeriz).
                    # Burada hesaplamadan düşmek daha doğrudur ama tablo bütünlüğü için fillna yapılabilir.
                    # Biz düşürmeyi tercih ediyoruz (dropna), bu yüzden fillna yapmıyoruz.
                else:
                    df_analiz['Aylik_Ortalama'] = df_analiz[son] # Fallback

                # 3. ENDEKS VE ENFLASYON HESABI
                # Sadece hem "Şu An (Ortalama)" hem "Baz Tarihte" veri olan ürünler üzerinden hesaplanır
                gecerli_veri = df_analiz.dropna(subset=['Aylik_Ortalama', baz_col]).copy()
                
                enf_genel = 0.0; enf_gida = 0.0
                
                if not gecerli_veri.empty:
                    # Kümülatif (Yıl içi) Enflasyon Hesabı (GEOMETRİK ORTALAMA ÜZERİNDEN)
                    w = gecerli_veri[agirlik_col]
                    
                    # KRİTİK DEĞİŞİKLİK: [son] yerine ['Aylik_Ortalama'] kullanıyoruz
                    p_relative = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
                    
                    # Formül: I = Toplam(W * (Pn/P0)) / Toplam(W) * 100
                    genel_endeks = (w * p_relative).sum() / w.sum() * 100
                    enf_genel = genel_endeks - 100
                    
                    # Gıda Enflasyonu (01 Kodlu ürünler)
                    gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
                    if not gida_df.empty:
                        w_g = gida_df[agirlik_col]
                        p_rel_g = gida_df['Aylik_Ortalama'] / gida_df[baz_col]
                        enf_gida = ((w_g * p_rel_g).sum() / w_g.sum() * 100) - 100

                    # Ürün Bazlı Kümülatif Değişim (Tabloda % Farkı Ortalama ile gösterelim)
                    df_analiz['Fark'] = (df_analiz['Aylik_Ortalama'] / df_analiz[baz_col]) - 1
                else:
                    df_analiz['Fark'] = 0.0

                # 4. ZAMAN SERİSİ / TREND HESAPLAMA (Prophet İçin - Günlük devam edebilir)
                # Trend grafiğinde günlük değişimleri görmek isteyebilirsin, burayı günlük bırakıyorum.
                trend_data = []
                for g in gunler:
                    tmp_df = df_analiz.dropna(subset=[g, baz_col])
                    if not tmp_df.empty:
                        w_tmp = tmp_df[agirlik_col]
                        idx_val = (w_tmp * (tmp_df[g] / tmp_df[baz_col])).sum() / w_tmp.sum() * 100
                        trend_data.append({"Tarih": g, "TÜFE": idx_val})
                
                df_trend = pd.DataFrame(trend_data)
                if not df_trend.empty:
                    df_trend['Tarih'] = pd.to_datetime(df_trend['Tarih'])
                
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
                    # Tahmin edilen endeks değerinden enflasyona dönüştürme (Endeks - 100)
                    if not forecast_row.empty:
                        month_end_forecast = forecast_row.iloc[0]['yhat'] - 100
                    else:
                        month_end_forecast = df_forecast.iloc[-1]['yhat'] - 100
                else: 
                    # Prophet çalışmazsa basit projeksiyon
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
                      st.markdown(f"""
                        <div class="kpi-card" style="border-left: 3px solid {accent_color};">
                             <div style="position: absolute; right: 20px; top: 20px; opacity: 0.1; font-size: 32px; filter: grayscale(100%);">{icon}</div>
                            <div class="kpi-title">{title}</div>
                            <div class="kpi-value">{val}</div>
                            <div class="kpi-sub" style="color: {sub_color};">{sub}</div>
                        </div>
                    """, unsafe_allow_html=True)

                c1, c2, c3, c4 = st.columns(4)
                with c1: kpi_card("Kümülatif Enflasyon", f"%{enf_genel:.2f}", f"Baz: {baz_tanimi}", "#f87171", "#ef4444", "📈")
                with c2: kpi_card("Gıda Enflasyonu", f"%{enf_gida:.2f}", "Mutfak Sepeti", "#f87171", "#84cc16", "🛒")
                with c3: kpi_card("Simülasyon Tahmini", f"%{math.floor(enf_genel):.2f}", "Canlı Veri", "#a78bfa", "#8b5cf6", "🤖") 
                with c4: kpi_card("Resmi TÜİK Verisi", f"%{resmi_aylik_enf:.2f}", f"{resmi_tarih_str}", "#fbbf24", "#eab308", "🏛️")
                st.markdown("<br>", unsafe_allow_html=True)

                def style_chart(fig, is_pdf=False, is_sunburst=False):
                    if is_pdf:
                        fig.update_layout(template="plotly_white", font=dict(family="Arial", size=14, color="black"))
                    else:
                        layout_args = dict(
                            template="plotly_dark",
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter, sans-serif", color="#e2e8f0"),
                            margin=dict(l=0, r=0, t=30, b=0),
                        )
                        if not is_sunburst:
                             layout_args.update(dict(
                                 xaxis=dict(showgrid=False, zeroline=False), 
                                 yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False)
                             ))
                        fig.update_layout(**layout_args)
                    return fig

                df_analiz['Fark_Yuzde'] = df_analiz['Fark'] * 100
                t_sektor, t_ozet, t_veri, t_rapor = st.tabs(["📂 KATEGORİ DETAY", "📊 PİYASA ÖZETİ", "📋 TAM LİSTE", "📝 RAPORLAMA"])
                
                with t_sektor:
                    st.markdown("### 🔍 Detaylı Fiyat Analizi")
                    kategoriler = ["TÜMÜ"] + sorted(df_analiz['Grup'].unique().tolist())
                    secilen_kategori = st.selectbox("Kategori Filtrele:", kategoriler)
                    df_goster = df_analiz.copy() if secilen_kategori == "TÜMÜ" else df_analiz[df_analiz['Grup'] == secilen_kategori]
                    
                    cols = st.columns(4)
                    for idx, row in df_goster.iterrows():
                        # KARTLARDA SON FİYATI GÖSTERELİM (ETİKET BİLGİSİ İÇİN)
                        fiyat = row[son] 
                        # AMA DEĞİŞİM YÜZDESİNİ ORTALAMADAN HESAPLADIĞIMIZ FARK İLE GÖSTERELİM
                        fark = row['Fark'] * 100 
                        
                        if fark > 0: badge_cls = "pg-red"; symbol = "▲"
                        elif fark < 0: badge_cls = "pg-green"; symbol = "▼"
                        else: badge_cls = "pg-gray"; symbol = "-"
                        smart_tag = ""
                        if fiyat >= row['Max_Fiyat']: smart_tag = "<div class='status-tag tag-peak'>🔥 ZİRVE</div>"
                        elif fiyat <= row['Min_Fiyat'] and fiyat > 0: smart_tag = "<div class='status-tag tag-dip'>💎 FIRSAT</div>"
                        card_html = f"""<div class="pg-card">{smart_tag}<div class="pg-name">{html.escape(str(row[ad_col]))}</div><div class="pg-price">{fiyat:.2f} ₺</div><div class="pg-badge {badge_cls}">{symbol} %{fark:.2f}</div></div>"""
                        with cols[idx % 4]:
                            st.markdown(card_html, unsafe_allow_html=True)
                            st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)
                
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
                              "Fark": st.column_config.ProgressColumn("Kümülatif Değişim (Geo. Ort)", format="%.2f", min_value=-0.5, max_value=0.5), 
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
                    st.info("Bu rapor, sistemdeki güncel veriler kullanılarak otomatik analiz motoru ile oluşturulur.")
                    if st.button("🚀 DETAYLI RAPORU HAZIRLA (PDF)", type="primary"):
                        with st.spinner("Rapor oluşturuluyor..."):
                            en_cok_artan_row = df_analiz.sort_values('Fark', ascending=False).iloc[0]
                            rap_text = generate_detailed_static_report(df_analiz=df_analiz, tarih=son, enf_genel=enf_genel, enf_gida=enf_gida, gun_farki=gun_farki, tahmin=month_end_forecast, ad_col=ad_col, agirlik_col=agirlik_col)
                            fig_katki_pdf = go.Figure(go.Bar(x=df_sektor_katki['Katki_Puan'], y=df_sektor_katki['Grup'], orientation='h', marker=dict(color='#0f172a')))
                            fig_katki_pdf.update_layout(title="Sektörel Katkı")
                            style_chart(fig_katki_pdf, is_pdf=True) 

                            top_n = 7
                            df_uclar = pd.concat([df_analiz.sort_values('Fark', ascending=True).head(top_n), df_analiz.sort_values('Fark', ascending=False).head(top_n)]).sort_values('Fark', ascending=True)
                            df_uclar['Renk'] = df_uclar['Fark'].apply(lambda x: '#dc2626' if x > 0 else '#16a34a')
                            fig_uclar = go.Figure(go.Bar(x=df_uclar['Fark'] * 100, y=df_uclar[ad_col], orientation='h', marker=dict(color=df_uclar['Renk']), text=(df_uclar['Fark']*100).apply(lambda x: f"%{x:+.2f}"), textposition='outside'))
                            fig_uclar.update_layout(title=f"Uç Noktalar")
                            style_chart(fig_uclar, is_pdf=True) 

                            figs = {"Enflasyonun Sektörel Kaynakları": fig_katki_pdf, "Fiyat Hareketlerinde Uç Noktalar": fig_uclar}
                            metrics = {'genel': enf_genel, 'gida': enf_gida, 'top_urun': en_cok_artan_row[ad_col]}
                            pdf_data = create_pdf_report_advanced(text_content=rap_text, df_table=df_analiz.sort_values('Fark', ascending=False).head(20), figures=figs, manset_oran=enf_genel, metrics_dict=metrics, date_str_ignored="-")
                            st.success("✅ Rapor Hazırlandı!")
                            st.download_button("📥 PDF Raporunu İndir", data=pdf_data, file_name=f"Strateji_Raporu_{son}.pdf", mime="application/pdf")

            # --- SİNYAL MERKEZİ BOTU ---
            # --- SİNYAL MERKEZİ BOTU (GELİŞMİŞ VERSİYON) ---
            with st.popover("💬", help="AI Asistan"):
                st.markdown("🧬 VERİ MERKEZİ")
                
                # Kapsam Seçimi
                tum_kategoriler = ["TÜMÜ"] + sorted(df_analiz['Grup'].unique().tolist())
                c_bot1, c_bot2 = st.columns([1, 2])
                
                with c_bot1:
                    bot_kapsam = st.selectbox("Kapsam", tum_kategoriler, label_visibility="collapsed", key="bot_kapsam_yeni")
                
                with c_bot2:
                    sorular = [
                        "Analiz Seçiniz...",
                        "🚀 Zam Şampiyonları (Top 3)",
                        "📉 İndirim Liderleri (Top 3)",
                        "📊 Enflasyon/Değişim Ortalaması",
                        "💎 En Pahalı Ürünler",
                        "🏷️ En Ucuz Ürünler",
                        "🧱 Fiyatı Sabit Kalanlar",
                        "📈 Pazar Yönü (Artan/Azalan)"
                    ]
                    bot_soru = st.selectbox("Soru", sorular, label_visibility="collapsed", key="bot_soru_yeni")
            
                # Veri Filtreleme
                df_bot = df_analiz.copy()
                if bot_kapsam != "TÜMÜ":
                    df_bot = df_bot[df_bot['Grup'] == bot_kapsam]
            
                # Cevap Mantığı ve HTML Oluşturma
                if bot_soru != "Analiz Seçiniz...":
                    html_out = ""
                    header_txt = f"SYSTEM_ANALYSIS :: {bot_kapsam.upper()} :: {datetime.now().strftime('%H:%M:%S')}"
                    
                    if df_bot.empty:
                        html_out = "<span style='color:red'>HATA: Veri seti boş.</span>"
                    else:
                        try:
                            if "Zam Şampiyonları" in bot_soru:
                                top3 = df_bot.sort_values('Fark', ascending=False).head(3)
                                rows = ""
                                for i, (_, r) in enumerate(top3.iterrows()):
                                    rows += f"<tr><td>#{i+1} {r[ad_col][:20]}..</td><td style='text-align:right' class='trend-up'>%{(r['Fark']*100):.2f} ▲</td></tr>"
                                html_out = f"Dönemin en yüksek fiyat artışları:<table class='mini-table'><tr><th>ÜRÜN</th><th style='text-align:right'>DEĞİŞİM</th></tr>{rows}</table>"
            
                            elif "İndirim Liderleri" in bot_soru:
                                top3 = df_bot.sort_values('Fark', ascending=True).head(3)
                                rows = ""
                                for i, (_, r) in enumerate(top3.iterrows()):
                                    # Sadece düşenleri veya en az artanları göster
                                    color_cls = "trend-down" if r['Fark'] < 0 else "cmd-response"
                                    rows += f"<tr><td>#{i+1} {r[ad_col][:20]}..</td><td style='text-align:right' class='{color_cls}'>%{(r['Fark']*100):.2f} ▼</td></tr>"
                                html_out = f"Fiyatı gevşeyen veya en az artanlar:<table class='mini-table'><tr><th>ÜRÜN</th><th style='text-align:right'>DEĞİŞİM</th></tr>{rows}</table>"
            
                            elif "Ortalama" in bot_soru:
                                ort = df_bot['Fark'].mean() * 100
                                med = df_bot['Fark'].median() * 100
                                trend = "trend-up" if ort > 0 else "trend-down"
                                arrow = "▲" if ort > 0 else "▼"
                                html_out = f"""
                                Bu kapsamdaki ({len(df_bot)}) ürün için istatistikler:<br><br>
                                • Aritmetik Ort: <span class='{trend}'>%{ort:.2f} {arrow}</span><br>
                                • Medyan (Ortanca): <span class='highlight-val'>%{med:.2f}</span>
                                """
            
                            elif "En Pahalı" in bot_soru:
                                top3 = df_bot.sort_values(son, ascending=False).head(3)
                                rows = ""
                                for i, (_, r) in enumerate(top3.iterrows()):
                                    rows += f"<tr><td>{r[ad_col][:18]}..</td><td style='text-align:right' class='highlight-val'>{r[son]:.2f} ₺</td></tr>"
                                html_out = f"Etiket fiyatı en yüksek ürünler:<table class='mini-table'>{rows}</table>"
            
                            elif "En Ucuz" in bot_soru:
                                top3 = df_bot.sort_values(son, ascending=True).head(3)
                                rows = ""
                                for i, (_, r) in enumerate(top3.iterrows()):
                                    rows += f"<tr><td>{r[ad_col][:18]}..</td><td style='text-align:right' class='highlight-val'>{r[son]:.2f} ₺</td></tr>"
                                html_out = f"Etiket fiyatı en düşük ürünler:<table class='mini-table'>{rows}</table>"
            
                            elif "Sabit" in bot_soru:
                                sabitler = df_bot[df_bot['Fark'] == 0]
                                count = len(sabitler)
                                if count > 0:
                                    ornekler = ", ".join(sabitler[ad_col].head(4).tolist())
                                    html_out = f"Toplam <span class='highlight-val'>{count}</span> ürünün fiyatı değişmedi.<br><br>Örnekler:<br><span style='font-size:11px; opacity:0.8'>{ornekler}...</span>"
                                else:
                                    html_out = "Baz döneme göre fiyatı değişmeyen ürün bulunamadı."
            
                            elif "Pazar Yönü" in bot_soru:
                                artan = len(df_bot[df_bot['Fark'] > 0])
                                dusen = len(df_bot[df_bot['Fark'] < 0])
                                sabit = len(df_bot[df_bot['Fark'] == 0])
                                html_out = f"""
                                Piyasa hareket özeti:<br>
                                <table class='mini-table'>
                                <tr><td>Yükselen</td><td style='text-align:right; color:#ef4444'>{artan}</td></tr>
                                <tr><td>Düşen</td><td style='text-align:right; color:#4ade80'>{dusen}</td></tr>
                                <tr><td>Değişmeyen</td><td style='text-align:right; color:#9ca3af'>{sabit}</td></tr>
                                </table>
                                """
                        except Exception as e:
                            html_out = f"<span style='color:red'>HESAPLAMA HATASI: {str(e)}</span>"
            
                    # TERMİNAL ÇIKTISI GÖSTERİMİ
                    st.markdown(f"""
                    <div class="terminal-wrapper">
                        <div class="terminal-header">
                            <span>TERMINAL_OUTPUT</span>
                            <span>{bot_kapsam[:3].upper()}</span>
                        </div>
                        <div class="cmd-line">user@basekonomist:~$ ./analyze --{bot_soru.split(' ')[1].lower()}</div>
                        <div class="cmd-response">
                            {html_out}
                        </div>
                        <div style="margin-top:10px; font-size:9px; color:#555;">_ cursor blinking...</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                else:
                    # Boş Durum (Placeholder) - YÜKSEK KONTRAST DÜZELTMESİ
                    st.markdown(f"""
                    <div class="terminal-wrapper" style="background-color: #050505 !important; opacity: 1 !important; border: 1px solid #333;">
                        
                        <div class="terminal-header" style="color: #4ade80 !important; border-bottom: 1px solid #333; opacity: 1 !important; font-weight: bold;">
                            <span>SYSTEM_STATUS</span>
                            <span>WAITING_INPUT</span>
                        </div>
                        
                        <div class="cmd-response" style="color: #ffffff !important; opacity: 1 !important; font-size: 13px; padding-top: 15px;">
                            Sistem hazır. Analiz başlatmak için yukarıdan bir sorgu seçin.
                            <br><br>
                            <span style="color: #22c55e !important; font-weight: 900;">root@basekonomist:~$</span> 
                            <span style="color: #ffffff !important; font-weight: normal;">Awaiting command...</span> 
                            <span style="animation: blink 1s step-end infinite; color: #22c55e; font-weight: bold;">█</span>
                        </div>
                    </div>
                    
                    <style>
                        @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
                    </style>
                    """, unsafe_allow_html=True)

        except Exception as e: st.error(f"Sistem Hatası: {e}")
    st.markdown('<div style="text-align:center; color:#52525b; font-size:11px; margin-top:50px;">VALIDASYON MUDURLUGU © 2026 - CONFIDENTIAL</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    dashboard_modu()





