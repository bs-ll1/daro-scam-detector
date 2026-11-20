import html

import requests
import streamlit as st

import theme

theme.setup("الحملات", "campaigns")

API = "http://127.0.0.1:8000"

theme.hero("كشف الحملات", "الاحتيالية", "الروابط المشبوهة التي تتشارك البنية نفسها تُجمَّع كحملة واحدة")

c1, c2 = st.columns(2)
if c1.button("📥 تحميل بيانات تجريبية للعرض"):
    requests.post(f"{API}/seed-demo", timeout=10)
if c2.button("🗑️ مسح كل البيانات"):
    requests.post(f"{API}/reset", timeout=10)

try:
    data = requests.get(f"{API}/campaigns", timeout=10).json()
except requests.exceptions.ConnectionError:
    st.error("السيرفر مو شغّال. شغّل uvicorn في التيرمنال الأول.")
    st.stop()

camps = data["campaigns"]
st.markdown(f"""<div class="stats" style="grid-template-columns:repeat(2,1fr)">
<div class="stat"><b>{data['total_seen']}</b><span>روابط مشبوهة مسجّلة</span></div>
<div class="stat"><b style="color:{theme.COLORS['bad']}">{len(camps)}</b><span>حملات مكتشفة</span></div>
</div>""", unsafe_allow_html=True)

if not camps:
    st.info("ما فيه حملات بعد. اضغط تحميل البيانات التجريبية، "
            "أو افحص عدة روابط مشبوهة من صفحة فحص الروابط.")

for i, c in enumerate(camps, 1):
    brands = html.escape("، ".join(c["brands"]) or "غير محدد")
    ips = html.escape("، ".join(c["ips"]) or "غير معروف")
    demo_tag = '<span class="tag"> · بيانات تجريبية</span>' if c["has_demo"] else ""
    st.markdown(
        f'<div class="camp"><b>حملة #{i}</b>{demo_tag}<br>'
        f'عدد الروابط: <b>{c["size"]}</b> &nbsp;|&nbsp; الجهة المنتحَلة: <b>{brands}</b> '
        f'&nbsp;|&nbsp; متوسط الخطورة: <b>{c["avg_risk"]}/100</b><br>'
        f'<span style="color:#8b97b3;direction:ltr;display:inline-block">IP: {ips}</span></div>',
        unsafe_allow_html=True)

    dot = ['digraph G { rankdir=LR; bgcolor="transparent";',
           'node [fontname="Arial", fontcolor="white", color="#c9a86a"];',
           'edge [color="#e5484d"];']
    for d in c["domains"]:
        dot.append(f'"{d["domain"]}" [shape=box, style=filled, fillcolor="#16203d"];')
        if d["ip"]:
            dot.append(f'"{d["ip"]}" [shape=ellipse, style=filled, fillcolor="#5a1d2b"];')
            dot.append(f'"{d["ip"]}" -> "{d["domain"]}";')
    dot.append("}")
    with st.expander(f"رسم العلاقات والتفاصيل (حملة #{i})"):
        st.graphviz_chart("\n".join(dot))
        for d in c["domains"]:
            st.markdown(f'`{d["domain"]}` — خطورة {d["risk"]} — {d["seen_at"]}')

theme.footer()