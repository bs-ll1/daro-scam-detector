import html
import streamlit as st

COLORS = {"ok": "#1fd1a5", "bad": "#ff5a67", "warn": "#f0b04a",
          "unk": "#8b8fd6", "info": "#5aa9e6"}

PAGES = [("home", "app.py", "🏠  الرئيسية"),
         ("links", "pages/links.py", "🔗  تحليل الروابط"),
         ("messages", "pages/messages.py", "💬  تحليل الرسائل"),
         ("visual", "pages/visual.py", "👁️  الفحص البصري"),
         ("campaigns", "pages/campaigns.py", "🕸️  ربط الحملات"),
         ("benchmark", "pages/benchmark.py", "📊  القياس")]

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');
html, body, .stApp, .stMarkdown, p, label, button, input, textarea, h1, h2, h3 {
  font-family:'Tajawal',sans-serif !important; }
.stApp { direction:rtl; color:#e8f0f7;
  background:radial-gradient(1000px 500px at 80% -10%, rgba(31,209,165,.10), transparent 60%),
             linear-gradient(180deg,#06101c 0%,#040a14 100%); }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stSidebarNav"] { display:none !important; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stAppViewContainer"] { flex-direction:row-reverse; }
.block-container { max-width:1100px; padding-top:1.2rem; padding-bottom:3rem; }

section[data-testid="stSidebar"] { width:270px !important; min-width:270px !important;
  background:linear-gradient(180deg,#071524,#050c18); border-left:1px solid rgba(31,209,165,.15); }
section[data-testid="stSidebar"] > div { padding-top:1rem; }
.sbrand { text-align:center; padding:6px 0 18px; border-bottom:1px solid rgba(255,255,255,.07);
  margin-bottom:14px; }
.sbrand b { display:block; font-size:1.5rem; font-weight:800; color:#e8fff8; margin-top:6px; }
.sbrand span { color:#7f93a8; font-size:.78rem; }
.sfoot { color:#5f748a; font-size:.78rem; text-align:center; margin-top:26px;
  border-top:1px solid rgba(255,255,255,.07); padding-top:14px; }
a[data-testid="stPageLink-NavLink"] { border-radius:12px; border:1px solid transparent;
  padding:9px 12px; color:#9db0c4; text-decoration:none; margin-bottom:4px; }
a[data-testid="stPageLink-NavLink"]:hover { background:rgba(31,209,165,.08); color:#e8fff8; }
a[data-testid="stPageLink-NavLink"][disabled], a[data-testid="stPageLink-NavLink"][aria-disabled="true"] {
  color:#1fd1a5; border-color:rgba(31,209,165,.45); background:rgba(31,209,165,.10);
  opacity:1; font-weight:700; }

.herobox { position:relative; overflow:hidden; border-radius:24px; padding:40px 34px;
  border:1px solid rgba(31,209,165,.25); margin-top:6px;
  background:radial-gradient(600px 300px at 15% 20%, rgba(31,209,165,.20), transparent 60%),
             radial-gradient(500px 300px at 90% 85%, rgba(90,169,230,.16), transparent 60%), #08121f; }
.herobox::before { content:""; position:absolute; inset:0; pointer-events:none;
  background-image:linear-gradient(rgba(255,255,255,.05) 1px, transparent 1px),
                   linear-gradient(90deg, rgba(255,255,255,.05) 1px, transparent 1px);
  background-size:34px 34px;
  -webkit-mask-image:radial-gradient(circle at 25% 40%, #000, transparent 70%);
  mask-image:radial-gradient(circle at 25% 40%, #000, transparent 70%); }
.herobox h1 { position:relative; margin:0; font-size:2.7rem; font-weight:800; color:#f2fffb; }
.herobox h1 em { font-style:normal; color:#1fd1a5; }
.herobox p { position:relative; margin:8px 0 0; color:#9db0c4; font-size:1.05rem; }
.herobox .tag { position:relative; display:inline-block; margin-top:14px; font-size:.78rem;
  color:#8fe9d0; border:1px solid rgba(31,209,165,.35); background:rgba(31,209,165,.08);
  padding:4px 12px; border-radius:99px; }

.hero { text-align:center; padding:22px 0 6px; }
.hero h1 { font-size:2.4rem; font-weight:800; margin:0; color:#f2fffb; }
.hero h1 em { font-style:normal; color:#1fd1a5; }
.hero p { color:#8aa0b6; margin:6px 0 0; }

.stats { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:18px 0 6px; }
.stats4 { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:18px 0 10px; }
.stat { border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:16px;
  background:rgba(255,255,255,.035); text-align:center; }
.stat b { display:block; font-size:2rem; font-weight:800; }
.stat span { color:#8aa0b6; font-size:.85rem; }
.sec { font-size:1.15rem; font-weight:800; margin:22px 0 8px; color:#e8fff8; }

[data-testid="stVerticalBlockBorderWrapper"] { border-radius:16px !important;
  border-color:rgba(255,255,255,.09) !important; background:rgba(255,255,255,.03); }
.tool b { font-size:1.05rem; color:#e8fff8; } .tool span { color:#8aa0b6; font-size:.86rem; }

.tbl { width:100%; border-collapse:collapse; font-size:.9rem; }
.tbl th { color:#7f93a8; font-weight:500; text-align:right; padding:8px 6px;
  border-bottom:1px solid rgba(255,255,255,.08); }
.tbl td { padding:9px 6px; border-bottom:1px solid rgba(255,255,255,.05); }
.tbl td.d { direction:ltr; text-align:left; color:#cfe0ee; }
.bdg { padding:2px 12px; border-radius:99px; font-size:.8rem; border:1px solid; }
.bdg.hi { color:#ff5a67; border-color:#ff5a67; background:rgba(255,90,103,.10); }
.bdg.md { color:#f0b04a; border-color:#f0b04a; background:rgba(240,176,74,.10); }

.stTextInput input, .stTextArea textarea { background:rgba(8,16,30,.9) !important;
  border:1px solid #223149 !important; border-radius:14px !important; color:#fff !important;
  padding:14px !important; font-size:1rem !important; }
.stTextInput input { direction:ltr; text-align:left; }
.stTextInput input:focus, .stTextArea textarea:focus { border-color:#1fd1a5 !important;
  box-shadow:0 0 0 3px rgba(31,209,165,.15) !important; }
.stButton>button, .stDownloadButton>button { width:100%; border-radius:12px; padding:11px;
  font-weight:700; border:1px solid #243650; background:rgba(12,22,40,.95); color:#d7e6f3;
  transition:.2s; }
.stButton>button:hover, .stDownloadButton>button:hover { border-color:#1fd1a5; color:#fff;
  transform:translateY(-1px); box-shadow:0 8px 22px -12px #1fd1a5; }

.scan { border:1px solid rgba(31,209,165,.30); border-radius:16px; padding:16px 22px;
  margin-top:14px; background:rgba(255,255,255,.03); position:relative; overflow:hidden; }
.scan::after { content:""; position:absolute; left:0; right:0; top:0; height:2px;
  background:linear-gradient(90deg,transparent,#1fd1a5,transparent); animation:sweep 1.5s linear infinite; }
@keyframes sweep { from{top:0;} to{top:100%;} }
.step { padding:4px 0; color:#7388a0; } .step.done { color:#1fd1a5; }
.step.now { color:#e8fff8; font-weight:700; }

.rcard { border-radius:22px; padding:26px 22px; margin:14px 0 12px; text-align:center;
  border:1px solid var(--c); background:rgba(255,255,255,.03);
  box-shadow:0 0 50px -18px var(--c); animation:rise .5s ease; }
@keyframes rise { from{opacity:0; transform:translateY(12px);} to{opacity:1; transform:none;} }
.gauge { position:relative; width:160px; height:160px; margin:0 auto; }
.gauge svg { transform:rotate(-90deg); }
.gbg { stroke:#14233a; }
.gfg { stroke:var(--c); stroke-linecap:round; stroke-dasharray:339.3;
  animation:fill 1.1s ease-out forwards; filter:drop-shadow(0 0 5px var(--c)); }
@keyframes fill { from{stroke-dashoffset:339.3;} to{stroke-dashoffset:var(--off);} }
.gnum { position:absolute; inset:0; display:flex; flex-direction:column; align-items:center;
  justify-content:center; font-size:2.7rem; font-weight:800; color:var(--c); }
.gnum small { font-size:.75rem; color:#8aa0b6; font-weight:500; }
.verdict { font-size:1.3rem; font-weight:800; margin:14px 0 2px; color:#f2fffb; }
.subt { direction:ltr; color:#8aa0b6; font-size:.92rem; }
.items { margin-top:10px; }
.item { text-align:right; background:rgba(255,255,255,.04); border-radius:12px;
  padding:10px 14px; margin-top:8px; border-right:3px solid var(--c); }
.item.ai { border-right-color:#8b8fd6; background:rgba(139,143,214,.08); }
.item.note { border-right-color:#33465f; color:#8aa0b6; font-size:.88rem; }
.lnk { direction:ltr; text-align:left; background:rgba(255,255,255,.04);
  border-radius:12px; padding:10px 14px; margin-top:8px; }
.camp { border:1px solid rgba(255,90,103,.55); border-radius:18px; padding:16px 20px;
  margin-top:14px; background:rgba(255,255,255,.03); box-shadow:0 0 40px -20px #ff5a67; }
.camp .tag { color:#1fd1a5; font-size:.8rem; }
.footer { text-align:center; color:#566a80; font-size:.8rem; margin-top:34px; }
</style>"""

LOGO = """<svg width="54" height="54" viewBox="0 0 64 64"><defs>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#7ff3d6"/><stop offset="1" stop-color="#119a7a"/></linearGradient></defs>
<path d="M32 4 56 13v18c0 15-10 25-24 29C18 56 8 46 8 31V13z" fill="none" stroke="url(#g)" stroke-width="3.5"/>
<path d="M32 16 46 21v10c0 9-6 15-14 18-8-3-14-9-14-18V21z" fill="url(#g)" opacity=".9"/>
<path d="M25 32l5 5 9-10" fill="none" stroke="#06101c" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>"""


def setup(title, active):
    st.set_page_config(page_title=f"{title} | درع", page_icon="🛡️", layout="wide",
                       initial_sidebar_state="expanded")
    st.markdown(CSS, unsafe_allow_html=True)
    with st.sidebar:
        st.markdown(f"""<div class="sbrand">{LOGO}<b>درع</b>
<span>منصة كشف الاحتيال الإلكتروني</span></div>""", unsafe_allow_html=True)
        for key, path, label in PAGES:
            st.page_link(path, label=label, disabled=(key == active))
        st.markdown('<div class="sfoot">مشروع هاكاثون · تحليل آلي أولي<br>يدعم التحقيق ولا يغني عن المراجعة البشرية</div>',
                    unsafe_allow_html=True)


def hero(title, gold_word, sub):
    st.markdown(f'<div class="hero"><h1>{title} <em>{gold_word}</em></h1><p>{sub}</p></div>',
                unsafe_allow_html=True)


def item(text, kind=""):
    return f'<div class="item {kind}">{html.escape(str(text))}</div>'


def result_card(score, color, label, subtitle, items_html=""):
    off = 339.3 * (1 - score / 100)
    return f"""<div class="rcard" style="--c:{color};--off:{off}">
<div class="gauge"><svg width="160" height="160" viewBox="0 0 120 120">
<circle class="gbg" cx="60" cy="60" r="54" fill="none" stroke-width="7"/>
<circle class="gfg" cx="60" cy="60" r="54" fill="none" stroke-width="7"/></svg>
<div class="gnum">{score}<small>من 100</small></div></div>
<div class="verdict">{label}</div>
<div class="subt">{html.escape(subtitle)}</div>
<div class="items">{items_html}</div></div>"""


def footer():
    st.markdown('<div class="footer">درع · أداة تحليل آلي أولي تدعم التحقيق ولا تُغني عن المراجعة البشرية</div>',
                unsafe_allow_html=True)