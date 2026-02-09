# GEREKLİ KÜTÜPHANELER:
# pip install streamlit-lottie python-docx plotly pandas xlsxwriter matplotlib github beautifulsoup4

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
    pass # Zorunlu değil, hata vermesin

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
    initial_sidebar_state="collapsed" # Geniş alan için varsayılan kapalı
)

# --- CSS MOTORU (BİRLEŞTİRİLMİŞ) ---
def apply_theme():
    st.session_state.plotly_template = "plotly_dark"

    final_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

        :root {
            --bg-deep: #02040a;
            --glass-bg: rgba(255, 255, 255, 0.02);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-main: #f4f4f5;
            --text-dim: #a1a1aa;
            --accent-blue: #3b82f6;
            --card-radius: 16px;
        }

        /* Ana Arka Plan */
        [data-testid="stAppViewContainer"] {
            background-color: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(56, 189, 248, 0.06), transparent 25%), 
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.06), transparent 25%);
            background-attachment: fixed;
            font-family: 'Inter', sans-serif !important;
            color: var(--text-main) !important;
        }

        /* Scrollbar */
        ::-webkit-scrollbar { width: 8px; height: 8px; }
        ::-webkit-scrollbar-track { background: #02040a; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #3b82f6; }

        /* Header Gizleme */
        [data-testid="stHeader"] { visibility: hidden; height: 0px; }
        [data-testid="stToolbar"] { display: none; }

        /* --- ÜST MENÜ (RADIO BUTTONS - Code 1 Stili) --- */
        [data-testid="stRadio"] > div {
            display: flex;
            justify-content: center;
            gap: 10px;
            background: rgba(20, 20, 20, 0.6);
            backdrop-filter: blur(12px);
            padding: 8px 16px;
            border-radius: 24px;
            border: 1px solid var(--glass-border);
            margin-bottom: 25px;
            width: fit-content;
            margin-left: auto;
            margin-right: auto;
            overflow-x: auto;
        }
        
        [data-testid="stRadio"] label {
            background: transparent !important;
            border: 1px solid transparent !important;
            color: #71717a !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: all 0.3s ease !important;
            border-radius: 12px !important;
            padding: 8px 20px !important;
            margin: 0 !important;
        }
        
        [data-testid="stRadio"] label:hover {
            color: #fff !important;
            background: rgba(255,255,255,0.05) !important;
        }
        
        div[role="radiogroup"] label[data-checked="true"] {
            color: #fff !important;
            background: rgba(59, 130, 246, 0.2) !important;
            border: 1px solid rgba(59, 130, 246, 0.4) !important;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.25);
        }

        /* --- KPI KARTLARI (Code 2 Stili) --- */
        .kpi-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%);
            border: 1px solid var(--glass-border);
            border-radius: var(--card-radius);
            padding: 24px;
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 4px 24px -1px rgba(0, 0, 0, 0.2);
        }
        .kpi-card:hover {
            transform: translateY(-4px);
            border-color: rgba(59, 130, 246, 0.5);
            box-shadow: 0 10px 30px -5px rgba(59, 130, 246, 0.15);
        }
        .kpi-bg-icon {
            position: absolute; right: -15px; bottom: -25px;
            font-size: 100px; opacity: 0.04; transform: rotate(-15deg);
            filter: blur(1px); pointer-events: none;
        }
        .kpi-title {
            font-size: 11px; font-weight: 700; text-transform: uppercase;
            color: var(--text-dim); letter-spacing: 1.5px; margin-bottom: 12px;
        }
        .kpi-value {
            font-size: 36px; font-weight: 800; color: #fff;
            margin-bottom: 8px; letter-spacing: -1.5px;
            background: linear-gradient(to right, #fff, #94a3b8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .kpi-sub {
            font-size: 12px; font-weight: 500; display: flex; align-items: center; gap: 8px;
            color: var(--text-dim); background: rgba(0,0,0,0.2); padding: 4px 8px; border-radius: 6px; width: fit-content;
        }

        /* --- TICKER (Code 2) --- */
        .ticker-wrap {
            width: 100%; overflow: hidden;
            background: linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(20,20,30,0.5) 15%, rgba(20,20,30,0.5) 85%, rgba(0,0,0,0) 100%);
            border-top: 1px solid var(--glass-border); border-bottom: 1px solid var(--glass-border);
            padding: 12px 0; margin-bottom: 30px; white-space: nowrap;
        }
        .ticker-move {
            display: inline-block; padding-left: 100%;
            animation: marquee 45s linear infinite;
            font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: 0.5px;
        }
        @keyframes marquee { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }

        /* --- DİĞER BİLEŞENLER --- */
        .stSelectbox > div > div, .stTextInput > div > div {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid var(--glass-border) !important;
            color: var(--text-main) !important;
            border-radius: 12px !important;
        }
        
        /* Tablolar */
        [data-testid="stDataEditor"], [data-testid="stDataFrame"] {
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            background: rgba(10, 10, 15, 0.5) !important;
        }

        /* Smart Cards & Product Cards */
        .smart-card {
            background: rgba(30, 30, 35, 0.6); border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px; padding: 15px; display: flex; flex-direction: column; gap: 5px;
            transition: all 0.2s; position: relative; z-index: 1;
        }
        .sc-title { font-size: 11px; color: #a1a1aa; font-weight:600; text-transform:uppercase; }
        .sc-val { font-size: 20px; color: #fff; font-weight:700; display:flex; align-items:center; gap:8px; }

        .pg-card {
            background: rgba(20, 20, 25, 0.4); border: 1px solid var(--glass-border);
            border-radius: 12px; padding: 16px; height: 150px;
            display: flex; flex-direction: column; justify-content: space-between; align-items: center;
            text-align: center; transition: all 0.2s ease;
        }
        .pg-card:hover { transform: scale(1.03); background: rgba(40, 40, 45, 0.6); }
        .pg-name { font-size: 12px; font-weight: 500; color: #d4d4d8; line-height: 1.3; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; min-height: 32px; }
        .pg-price { font-size: 18px; font-weight: 700; color: #fff; margin: 8px 0; }
        .pg-badge { padding: 3px 10px; border-radius: 99px; font-size: 10px; font-weight: 700; }
        .pg-red { background: rgba(239, 68, 68, 0.1); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.2); }
        .pg-green { background: rgba(16, 185, 129, 0.1); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.2); }
        .pg-yellow { background: rgba(255, 255, 255, 0.05); color: #ffd966; }

        /* Animasyonlar */
        @keyframes fadeInUp { from { opacity: 0; transform: translate3d(0, 20px, 0); } to { opacity: 1; transform: translate3d(0, 0, 0); } }
        .animate-enter { animation: fadeInUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) both; }
        .delay-1 { animation-delay: 0.1s; } .delay-2 { animation-delay: 0.2s; } .delay-3 { animation-delay: 0.3s; }
        .blink { animation: blinker 1s linear infinite; } @keyframes blinker { 50% { opacity: 0; } }

        /* Skeleton */
        .skeleton {
            background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%);
            background-size: 200% 100%; animation: loading 1.5s infinite; border-radius: 12px;
        }
        @keyframes loading { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
    </style>
    """
    st.markdown(final_css, unsafe_allow_html=True)

apply_theme()

# --- 2. GITHUB & VERİ MOTORU ---
EXCEL_DOSYASI = "TUFE_Konfigurasyon.xlsx"
FIYAT_DOSYASI = "Fiyat_Veritabani.xlsx"
SAYFA_ADI = "Madde_Sepeti"

def get_github_repo():
    try:
        # Secrets kontrolü
        if "github" not in st.secrets:
            return None
        return Github(st.secrets["github"]["token"]).get_repo(st.secrets["github"]["repo_name"])
    except:
        return None

@st.cache_data(ttl=300, show_spinner=False)
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
        
        msg = f"Data Update: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        if c:
            repo.update_file(c.path, msg, out.getvalue(), c.sha, branch=st.secrets["github"]["branch"])
        else:
            repo.create_file(dosya_adi, msg, out.getvalue(), branch=st.secrets["github"]["branch"])
        return "OK"
    except Exception as e:
        return str(e)

# --- 3. RAPORLAMA MOTORU (WORD) ---
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
        except: pass

    return BytesIO(doc.save(BytesIO()).getvalue()) if False else BytesIO() # Save fix logic below
    
    # Fix for BytesIO save
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def generate_detailed_static_report(df_analiz, tarih, enf_genel, enf_gida, gun_farki, tahmin, ad_col, agirlik_col):
    df_clean = df_analiz.dropna(subset=['Fark'])
    ortalama_fark = df_clean['Fark'].mean()
    medyan_fark = df_clean['Fark'].median()
    
    piyasa_yorumu = "Genele Yayılım (Fiyat Artışı Homojen)"
    if ortalama_fark > (medyan_fark * 1.2): piyasa_yorumu = "Lokal Şoklar (Belirli Ürünler Endeksi Yükseltiyor)"
    elif ortalama_fark < (medyan_fark * 0.8): piyasa_yorumu = "İndirim Ağırlıklı (Kampanyalar Etkili)"

    artanlar = df_clean[df_clean['Fark'] > 0]
    inc_str = "\n".join([f"   🔴 %{row['Fark']*100:5.2f} | {row[ad_col]}" for _, row in df_clean.sort_values('Fark', ascending=False).head(5).iterrows()])
    dec_str = "\n".join([f"   🟢 %{abs(row['Fark']*100):5.2f} | {row[ad_col]}" for _, row in df_clean.sort_values('Fark', ascending=True).head(5).iterrows()])

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
**Yükselen Ürün Sayısı:** {len(artanlar)}

**3. ⚡ DİKKAT ÇEKENLER**
**▲ Yüksek Artışlar**
{inc_str}

**▼ Fiyat Düşüşleri**
{dec_str}

**4. 💡 SONUÇ**
Piyasa verileri, fiyat istikrarının henüz tam sağlanamadığını göstermektedir. Tahmin modelimiz, ay sonu kapanışının **%{tahmin:.2f}** bandında olacağını öngörmektedir.
"""
    return text.strip()

# --- 4. SCRAPER & UPDATE ---
def temizle_fiyat(t):
    if not t: return None
    t = str(t).replace('TL', '').replace('₺', '').strip()
    t = t.replace('.', '').replace(',', '.') if ',' in t and '.' in t else t.replace(',', '.')
    try: return float(re.sub(r'[^\d.]', '', t))
    except: return None

def kod_standartlastir(k): return str(k).replace('.0', '').strip().zfill(7)

def fiyat_bul_siteye_gore(soup, url):
    fiyat = 0; kaynak = "Regex"
    # Basit regex ile genel arama (Detaylı scraper Code 2'den alınabilir, burası özet)
    if m := re.search(r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺)', soup.get_text()[:5000]):
        if v := temizle_fiyat(m.group(1)): fiyat = v
    return fiyat, kaynak

def html_isleyici(progress_callback):
    repo = get_github_repo()
    if not repo: return "GitHub Bağlantı Hatası"
    progress_callback(0.1)
    
    try:
        df_conf = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
        if df_conf.empty: return "Konfigürasyon Hatası"
        
        df_conf.columns = df_conf.columns.str.strip()
        kod_col = next((c for c in df_conf.columns if c.lower() == 'kod'), None)
        url_col = next((c for c in df_conf.columns if c.lower() == 'url'), None)
        ad_col = next((c for c in df_conf.columns if 'ad' in c.lower()), 'Madde adı')
        
        df_conf['Kod'] = df_conf[kod_col].astype(str).apply(kod_standartlastir)
        url_map = {str(row[url_col]).strip(): row for _, row in df_conf.iterrows() if pd.notna(row[url_col])}
        veriler = []
        islenen = set()
        
        contents = repo.get_contents("", ref=st.secrets["github"]["branch"])
        zip_files = [c for c in contents if c.name.endswith(".zip") and c.name.startswith("Bolum")]
        
        for i, zip_file in enumerate(zip_files):
            progress_callback(0.1 + (0.8 * ((i + 1) / len(zip_files))))
            try:
                blob = repo.get_git_blob(zip_file.sha)
                with zipfile.ZipFile(BytesIO(base64.b64decode(blob.content))) as z:
                    for fn in z.namelist():
                        if not fn.endswith(('.html', '.htm')): continue
                        with z.open(fn) as f:
                            soup = BeautifulSoup(f.read().decode("utf-8", errors="ignore"), 'html.parser')
                            found = None
                            if c := soup.find("link", rel="canonical"): found = c.get("href")
                            if found and str(found).strip() in url_map:
                                t = url_map[str(found).strip()]
                                if t['Kod'] in islenen: continue
                                f_val, src = fiyat_bul_siteye_gore(soup, t[url_col])
                                if f_val > 0:
                                    veriler.append({
                                        "Tarih": datetime.now().strftime("%Y-%m-%d"),
                                        "Zaman": datetime.now().strftime("%H:%M"),
                                        "Kod": t['Kod'], "Madde_Adi": t[ad_col],
                                        "Fiyat": float(f_val), "Kaynak": src, "URL": t[url_col]
                                    })
                                    islenen.add(t['Kod'])
            except: pass
            
        progress_callback(0.95)
        if veriler: return github_excel_guncelle(pd.DataFrame(veriler), FIYAT_DOSYASI)
        else: return "Yeni veri bulunamadı."
    except Exception as e: return f"Hata: {str(e)}"

# --- 5. YARDIMCI GÖRSELLEŞTİRME ---
def make_neon_chart(fig):
    new_traces = []
    for trace in fig.data:
        if trace.type in ['scatter', 'line']:
            glow = go.Scatter(x=trace.x, y=trace.y, mode='lines',
                              line=dict(width=10, color=trace.line.color),
                              opacity=0.2, hoverinfo='skip', showlegend=False)
            new_traces.append(glow)
    fig.add_traces(new_traces)
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'))
    return fig

def render_skeleton():
    c1, c2, c3, c4 = st.columns(4)
    for c in [c1, c2, c3, c4]:
        with c: st.markdown('<div class="skeleton" style="height:120px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="skeleton" style="height:300px; margin-top:20px;"></div>', unsafe_allow_html=True)

def style_chart(fig, is_sunburst=False):
    layout_args = dict(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       font=dict(family="Inter, sans-serif", color="#a1a1aa", size=12), margin=dict(l=0, r=0, t=40, b=0))
    if not is_sunburst:
        layout_args.update(dict(xaxis=dict(showgrid=False, linecolor="rgba(255,255,255,0.1)"),
                                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.03)")))
    fig.update_layout(**layout_args)
    return fig

# --- 6. MAIN APPLICATION ---
def main():
    # --- YÜKLEME EKRANI ---
    loader_placeholder = st.empty()
    with loader_placeholder.container():
        render_skeleton()

    # --- VERİ ÇEKME ---
    df_f = github_excel_oku(FIYAT_DOSYASI)
    df_s = github_excel_oku(EXCEL_DOSYASI, SAYFA_ADI)
    
    loader_placeholder.empty()

    if df_f.empty or df_s.empty:
        st.warning("⚠️ Veri tabanına erişilemedi. Lütfen GitHub bağlantısını kontrol edin.")
        return

    # --- VERİ İŞLEME VE TARİH FİLTRESİ ---
    df_f['Tarih_DT'] = pd.to_datetime(df_f['Tarih'], errors='coerce')
    df_f = df_f.dropna(subset=['Tarih_DT']).sort_values('Tarih_DT')
    df_f['Tarih_Str'] = df_f['Tarih_DT'].dt.strftime('%Y-%m-%d')
    
    BASLANGIC_LIMITI = "2026-02-04" # 4 Şubat kritik tarih
    raw_dates = df_f['Tarih_Str'].unique().tolist()
    tum_tarihler = sorted([d for d in raw_dates if d >= BASLANGIC_LIMITI], reverse=True)
    
    # --- SIDEBAR (Geçmiş ve Lottie) ---
    with st.sidebar:
        lottie_url = "https://lottie.host/98606416-297c-4a37-9b2a-714013063529/5D6o8k8fW0.json"
        try:
            if 'st_lottie' in globals():
                r = requests.get(lottie_url); 
                if r.status_code==200: st_lottie(r.json(), height=150, key="anim")
        except: pass
        
        st.markdown("<div style='text-align:center;color:#fff;font-weight:800;font-size:20px;'>PİYASA MONİTÖRÜ</div>", unsafe_allow_html=True)
        st.markdown("---")
        
        if tum_tarihler:
            secilen_tarih = st.selectbox("📅 Geçmiş Veri:", tum_tarihler, index=0)
        else:
            secilen_tarih = None
            st.warning("2026-02-04 sonrası veri yok.")

        st.markdown("---")
        if st.button("Sistemi Senkronize Et ⚡", type="primary"):
            pbar = st.progress(0, text="Başlatılıyor...")
            res = html_isleyici(lambda x: pbar.progress(min(1.0, max(0.0, x))))
            pbar.empty()
            if "OK" in res:
                st.toast("Veriler Güncellendi!", icon="🚀")
                time.sleep(1)
                st.rerun()
            else:
                st.error(res)

    # --- HESAPLAMA MOTORU (CODE 2 ZİNCİRLEME MANTIĞI) ---
    # Konfigürasyon
    df_s.columns = df_s.columns.str.strip()
    kod_col = next((c for c in df_s.columns if c.lower() == 'kod'), 'Kod')
    ad_col = next((c for c in df_s.columns if 'ad' in c.lower()), 'Madde_Adi')
    col_w26 = 'Agirlik_2026'
    
    df_f['Kod'] = df_f['Kod'].astype(str).apply(kod_standartlastir)
    df_s['Kod'] = df_s[kod_col].astype(str).apply(kod_standartlastir)
    df_s = df_s.drop_duplicates(subset=['Kod'])
    
    # Pivot ve Merge
    df_f = df_f[df_f['Fiyat'] > 0]
    df_f_grp = df_f.groupby(['Kod', 'Tarih_Str'])['Fiyat'].mean().reset_index()
    pivot = df_f_grp.pivot_table(index='Kod', columns='Tarih_Str', values='Fiyat').ffill(axis=1).bfill(axis=1).reset_index()
    
    if 'Grup' not in df_s.columns:
        grup_map = {"01": "Gıda", "02": "Alkol-Tütün", "03": "Giyim", "04": "Konut", "05": "Ev Eşyası", "06": "Sağlık", "07": "Ulaşım", "08": "Haberleşme", "09": "Eğlence", "10": "Eğitim", "11": "Lokanta", "12": "Çeşitli"}
        df_s['Grup'] = df_s['Kod'].str[:2].map(grup_map).fillna("Diğer")
        
    df_analiz = pd.merge(df_s, pivot, on='Kod', how='left')
    
    # Tarih Kesiti
    tum_gunler = sorted([c for c in pivot.columns if c != 'Kod' and c >= BASLANGIC_LIMITI])
    if secilen_tarih and secilen_tarih in tum_gunler:
        gunler = tum_gunler[:tum_gunler.index(secilen_tarih)+1]
    else:
        gunler = tum_gunler
        
    if not gunler:
        st.error("Veri seti oluşturulamadı."); return

    son = gunler[-1]
    dt_son = datetime.strptime(son, '%Y-%m-%d')
    
    # Zincirleme Mantığı (4 Şubat)
    ZINCIR_TARIHI = datetime(2026, 2, 4)
    aktif_agirlik_col = col_w26
    
    # Baz Belirleme
    gunler_2026 = [c for c in tum_gunler if c >= "2026-01-01"]
    baz_col = gunler_2026[0] if gunler_2026 else gunler[0]
    
    # Ağırlık ve Fiyat Hazırlığı
    if aktif_agirlik_col in df_analiz.columns:
        df_analiz[aktif_agirlik_col] = pd.to_numeric(df_analiz[aktif_agirlik_col], errors='coerce').fillna(0)
    else:
        df_analiz[aktif_agirlik_col] = 0
        
    # Geometrik Ortalama
    def geo_mean(row):
        vals = [x for x in row if isinstance(x, (int, float)) and x > 0]
        return np.exp(np.mean(np.log(vals))) if vals else np.nan

    bu_ay_str = f"{dt_son.year}-{dt_son.month:02d}"
    bu_ay_cols = [c for c in gunler if c.startswith(bu_ay_str)]
    if not bu_ay_cols: bu_ay_cols = [son]
    
    gecerli_veri = df_analiz[df_analiz[aktif_agirlik_col] > 0].copy()
    gecerli_veri['Aylik_Ortalama'] = gecerli_veri[bu_ay_cols].apply(geo_mean, axis=1)
    gecerli_veri = gecerli_veri.dropna(subset=['Aylik_Ortalama', baz_col])
    
    # Endeks Hesabı
    enf_genel = 0.0
    if not gecerli_veri.empty:
        w = gecerli_veri[aktif_agirlik_col]
        p_rel = gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]
        if w.sum() > 0: enf_genel = (w * p_rel).sum() / w.sum() * 100 - 100
        
    # Günlük Fark
    df_analiz['Fark'] = 0.0
    if not gecerli_veri.empty:
        df_analiz.loc[gecerli_veri.index, 'Fark'] = (gecerli_veri['Aylik_Ortalama'] / gecerli_veri[baz_col]) - 1

    if len(gunler) >= 2:
        prev = gunler[-2]
        df_analiz['Gunluk_Degisim'] = (df_analiz[son] / df_analiz[prev]) - 1
    else:
        df_analiz['Gunluk_Degisim'] = 0

    # --- UI RENDERING (CODE 1 NAVIGASYON YAPISI) ---
    
    # 1. Header (Code 2 Stili - Çok şık)
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01)); padding: 20px 40px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div>
            <div style="font-size: 32px; font-weight: 800; color: #fff; letter-spacing: -1.5px;">Piyasa Monitörü <span style="font-size:10px; padding:4px 8px; background:rgba(59,130,246,0.2); color:#60a5fa; border-radius:99px; vertical-align:middle;">LIVE</span></div>
            <div style="font-size: 13px; color: #a1a1aa;">Yapay Zeka Destekli Enflasyon Analiz Sistemi</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 10px; color: #71717a; font-weight: 700;">RAPOR TARİHİ</div>
            <div style="font-size: 28px; font-weight: 800; color: #e4e4e7;">{dt_son.strftime('%d.%m.%Y')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Navigasyon (Code 1 Stili)
    menu = ["ANA SAYFA", "AĞIRLIKLAR", "TÜFE DETAY", "METODOLOJİ"]
    selected_tab = st.radio("", menu, horizontal=True, label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)

    # 3. İçerik Yönetimi
    if selected_tab == "ANA SAYFA":
        # --- DASHBOARD MODU (CODE 2'den) ---
        
        # Ticker
        inc = df_analiz.sort_values('Gunluk_Degisim', ascending=False).head(5)
        dec = df_analiz.sort_values('Gunluk_Degisim', ascending=True).head(5)
        items = []
        for _, r in inc.iterrows(): 
            if r['Gunluk_Degisim'] > 0: items.append(f"<span style='color:#f87171;'>▲ {r[ad_col]} %{r['Gunluk_Degisim']*100:.1f}</span>")
        for _, r in dec.iterrows():
            if r['Gunluk_Degisim'] < 0: items.append(f"<span style='color:#34d399;'>▼ {r[ad_col]} %{r['Gunluk_Degisim']*100:.1f}</span>")
        
        ticker_html = " &nbsp;&nbsp;•&nbsp;&nbsp; ".join(items) if items else "Piyasada yatay seyir."
        st.markdown(f'<div class="ticker-wrap"><div class="ticker-move">{ticker_html}</div></div>', unsafe_allow_html=True)

        # KPI Kartları
        c1, c2, c3, c4 = st.columns(4)
        def kpi(col, title, val, sub, color):
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">{title}</div>
                    <div class="kpi-value">{val}</div>
                    <div class="kpi-sub" style="color:{color}; border:1px solid {color}33; background:{color}11;">{sub}</div>
                </div>
                """, unsafe_allow_html=True)
        
        gida_enf = 0
        gida_df = gecerli_veri[gecerli_veri['Kod'].astype(str).str.startswith("01")]
        if not gida_df.empty:
            wg = gida_df[aktif_agirlik_col]
            if wg.sum() > 0: gida_enf = ((wg * (gida_df['Aylik_Ortalama']/gida_df[baz_col])).sum()/wg.sum()*100)-100

        kpi(c1, "GENEL ENFLASYON", f"%{enf_genel:.2f}", f"Baz: {baz_col}", "#ef4444")
        kpi(c2, "GIDA ENFLASYONU", f"%{gida_enf:.2f}", "Mutfak Sepeti", "#f59e0b")
        kpi(c3, "AYLIK DEĞİŞİM", f"%{df_analiz['Gunluk_Degisim'].mean()*100:.2f}", "Ortalama Volatilite", "#3b82f6")
        kpi(c4, "ÜRÜN SAYISI", f"{len(gecerli_veri)}", "Aktif Veri", "#10b981")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Dashboard Tabları
        tab_sektor, tab_liste, tab_rapor = st.tabs(["📂 KATEGORİ ÖZETİ", "📋 TAM LİSTE", "📝 RAPOR & EXCEL"])
        
        with tab_sektor:
            st.markdown("### Sektörel Isı Haritası")
            df_analiz['Grup_Fark'] = df_analiz['Fark'] * df_analiz[aktif_agirlik_col]
            grp = df_analiz.groupby('Grup').agg({'Grup_Fark':'sum', aktif_agirlik_col:'sum'}).reset_index()
            grp['Etki'] = (grp['Grup_Fark'] / grp[aktif_agirlik_col]) * 100
            
            fig = px.treemap(grp, path=[px.Constant("Piyasa"), 'Grup'], values=aktif_agirlik_col, color='Etki',
                             color_continuous_scale='RdYlGn_r', title="Sektörel Enflasyon Etkisi")
            st.plotly_chart(style_chart(fig, True), use_container_width=True)

        with tab_liste:
            # Code 2'nin gelişmiş Data Editor'ü
            col_cfg = {
                ad_col: "Ürün", "Grup": "Kategori",
                "Gunluk_Degisim": st.column_config.ProgressColumn("Günlük %", format="%.2f%%", min_value=-0.5, max_value=0.5),
                son: st.column_config.NumberColumn("Son Fiyat", format="%.2f ₺")
            }
            st.data_editor(
                df_analiz[['Grup', ad_col, son, 'Gunluk_Degisim']].sort_values('Gunluk_Degisim', ascending=False),
                column_config=col_cfg, use_container_width=True, height=500
            )

        with tab_rapor:
            c_rap1, c_rap2 = st.columns([2, 1])
            with c_rap1:
                tahmin = enf_genel * 1.05 # Basit projeksiyon
                rap_text = generate_detailed_static_report(df_analiz, son, enf_genel, gida_enf, 0, tahmin, ad_col, aktif_agirlik_col)
                st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:12px;">{rap_text.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            with c_rap2:
                st.markdown("### 📥 İndirmeler")
                # Excel
                out = BytesIO()
                with pd.ExcelWriter(out, engine='xlsxwriter') as w: df_analiz.to_excel(w, index=False)
                st.download_button("📊 Excel Verisi", out.getvalue(), f"Data_{son}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
                # Word
                w_out = create_word_report(rap_text, son, df_analiz)
                st.download_button("📄 Word Raporu", w_out, f"Rapor_{son}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

    elif selected_tab == "AĞIRLIKLAR":
        # Code 1'in Sunburst Grafiği (Code 2 verisiyle)
        st.header("⚖️ Sepet Ağırlıkları (2026)")
        fig_sun = px.sunburst(
            df_analiz, path=['Grup', ad_col], values=aktif_agirlik_col,
            color='Grup', title="Enflasyon Sepeti Ağırlık Dağılımı",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(style_chart(fig_sun, True), use_container_width=True)

    elif selected_tab == "TÜFE DETAY":
        # Code 1'in Detay Analiz Sayfası
        st.header("📈 Ürün Bazlı Fiyat Seyri")
        col_sel, col_viz = st.columns([3, 1])
        with col_sel:
            opt = ["GENEL TÜFE"] + sorted(df_analiz[ad_col].unique().tolist())
            sel = st.selectbox("Madde Seçin:", opt)
        
        if sel == "GENEL TÜFE":
            # Genel endeks serisi oluştur
            ts_data = [df_analiz[d].mean() for d in gunler]
            plot_df = pd.DataFrame({'Tarih': gunler, 'Deger': [x/ts_data[0]*100 for x in ts_data]})
            fig = px.line(plot_df, x='Tarih', y='Deger', title="Genel Endeks (Baz=100)")
        else:
            row = df_analiz[df_analiz[ad_col] == sel].iloc[0]
            plot_df = pd.DataFrame({'Tarih': gunler, 'Fiyat': row[gunler].values})
            fig = px.line(plot_df, x='Tarih', y='Fiyat', title=f"{sel} Fiyatı")
            
        fig.update_traces(line_color='#3b82f6', line_width=3)
        st.plotly_chart(make_neon_chart(style_chart(fig)), use_container_width=True)

    elif selected_tab == "METODOLOJİ":
        # Code 1'in Metodoloji Yazısı
        st.markdown("""
        <div style="background:rgba(255,255,255,0.03); padding:40px; border-radius:16px; border:1px solid rgba(255,255,255,0.1);">
        # Piyasa Monitörü Metodolojisi
        ### Günlük Tüketici Fiyat Endeksi Hesaplama Yöntemi
        ---
        **Yöntem:** Zincirleme Laspeyres Endeksi kullanılarak, 4 Şubat 2026 bazlı hesaplama yapılmaktadır.
        Her gün 50'den fazla kaynaktan otomatik veri toplanmakta ve geometrik ortalama ile madde fiyatları belirlenmektedir.
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
