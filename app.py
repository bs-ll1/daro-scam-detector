import html

import requests
import streamlit as st

import theme

theme.setup("الرئيسية", "home")
C = theme.COLORS

try:
    s = requests.get("http://127.0.0.1:8000/stats", timeout=10).json()
except Exception:
    st.error("السيرفر مو شغّال. شغّل uvicorn في التيرمنال الأول.")
    st.stop()

st.markdown("""<div class="herobox">
<h1>درع <em>·</em> منصة كشف الاحتيال</h1>
<p>نكشف الروابط والرسائل المنتحِلة للجهات الرسمية، ونربطها بالحملات التي تقف خلفها</p>
<span class="tag">مشروع هاكاثون · تحليل آلي أولي</span></div>""", unsafe_allow_html=True)

st.page_link("pages/links.py", label="ابدأ التحليل الآن  ←")

st.markdown(f"""<div class="stats4">
<div class="stat"><b>{s['checks']}</b><span>إجمالي الفحوصات</span></div>
<div class="stat"><b style="color:{C['bad']}">{s['suspicious']}</b><span>روابط مشبوهة مسجّلة</span></div>
<div class="stat"><b style="color:{C['info']}">{s['campaigns']}</b><span>حملات مرتبطة</span></div>
<div class="stat"><b style="color:{C['warn']}">{s['high']}</b><span>تنبيهات عالية الخطورة</span></div>
</div>""", unsafe_allow_html=True)

st.markdown('<div class="sec">⚡ أدوات التحليل</div>', unsafe_allow_html=True)
TOOLS = [("🔗 فاحص الروابط", "تحليل الروابط والدومينات وانتحال الجهات", "pages/links.py"),
                ("👁️ الفحص البصري", "مقارنة تصميم الصفحة بالصفحة الرسمية", "pages/visual.py"),
         ("💬 فاحص الرسائل", "تحليل رسائل SMS وواتساب", "pages/messages.py"),
         ("🕸️ ربط الحملات", "كشف الشبكات الاحتيالية المشتركة", "pages/campaigns.py")]
for row in (TOOLS[:2], TOOLS[2:]):
    cols = st.columns(2)
    for col, (name, desc, path) in zip(cols, row):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="tool"><b>{name}</b><br><span>{desc}</span></div>',
                            unsafe_allow_html=True)
                st.page_link(path, label="افتح  ←")

left, right = st.columns([2, 3])

with left:
    st.markdown('<div class="sec">🛡️ آخر نتيجة تحليل</div>', unsafe_allow_html=True)
    hist = st.session_state.get("hist", [])
    if hist:
        d, score, label = hist[0]
        color = C["bad"] if score >= 75 else C["warn"] if score >= 40 else C["ok"]
        st.markdown(theme.result_card(score, color, label, d), unsafe_allow_html=True)
    else:
        st.info("ما فيه فحوصات في هذه الجلسة بعد. جرّب فاحص الروابط.")

with right:
    st.markdown('<div class="sec">📋 آخر الحالات المكتشفة</div>', unsafe_allow_html=True)
    if s["recent"]:
        rows = ""
        for r in s["recent"]:
            lvl = '<span class="bdg hi">مرتفع</span>' if r["risk"] >= 75 \
                else '<span class="bdg md">متوسط</span>'
            demo = " (تجريبي)" if r["demo"] else ""
            rows += (f'<tr><td class="d">{html.escape(r["domain"])}</td>'
                     f'<td>{html.escape(r["brand"] or "غير محدد")}{demo}</td>'
                     f'<td>{lvl}</td><td>{html.escape(r["seen_at"])}</td></tr>')
        st.markdown(f"""<table class="tbl"><tr><th>النطاق</th><th>الجهة</th>
<th>الخطورة</th><th>التاريخ</th></tr>{rows}</table>""", unsafe_allow_html=True)
    else:
        st.info("ما فيه حالات مسجّلة. فحص رابط مشبوه أو حمّل بيانات تجريبية من صفحة الحملات.")

theme.footer()