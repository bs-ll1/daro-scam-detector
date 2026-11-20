import base64

import requests
import streamlit as st

import theme

theme.setup("التحليل البصري", "visual")

API = "http://127.0.0.1:8000/visual-check"
C = theme.COLORS

theme.hero("التحليل", "البصري", "نفتح الرابط في متصفح معزول ونقارن تصميمه بالصفحة الرسمية")

BRANDS = {"salik": "سالك", "adpolice": "شرطة أبوظبي", "dubaipolice": "شرطة دبي",
          "uaepass": "الهوية الرقمية UAE PASS", "icp": "الهوية والجنسية",
          "adcb": "بنك أبوظبي التجاري", "emiratesnbd": "الإمارات دبي الوطني",
          "adib": "مصرف أبوظبي الإسلامي", "mashreq": "المشرق", "rakbank": "راك بنك"}

brand = st.selectbox("الجهة المراد المقارنة معها", list(BRANDS),
                     format_func=lambda k: BRANDS[k])
url = st.text_input("الرابط المشبوه", placeholder="https://example.com")

if st.button("ابدأ التحليل البصري"):
    if not url.strip():
        st.info("اكتب رابطاً أولاً")
        st.stop()
    try:
        with st.spinner("جاري فتح الصفحتين وأخذ اللقطات (قد يستغرق دقيقة في أول مرة)..."):
            r = requests.post(API, json={"url": url, "brand": brand},
                              timeout=120).json()
    except requests.exceptions.ConnectionError:
        st.error("السيرفر مو شغّال. شغّل uvicorn في التيرمنال الأول.")
        st.stop()

    if not r.get("ok"):
        st.warning(r.get("error", "حدث خطأ"))
        st.stop()

    strong = r.get("strong", 0)
    if strong >= 3:
        color = C["bad"]
    elif strong == 2:
        color = C["warn"]
    else:
        color = C["ok"]
    label = r["verdict"]
    score = r["similarity"]

    items = theme.item(f"تشابه البصمة البصرية: {r['hash_sim']}% | تشابه الألوان: {r['color_sim']}%")
    for f in r.get("findings", []):
        items += theme.item("✔ " + f)
    ai = r.get("ai")
    if ai and "reason_ar" in ai:
        items += theme.item(f"تحليل الذكاء الاصطناعي: {ai['reason_ar']}", "ai")
    elif ai and "error" in ai:
        items += theme.item("تعذّر التحليل بالذكاء الاصطناعي، النتيجة من الفحص الآلي فقط.", "note")
    else:
        items += theme.item("طبقة الذكاء الاصطناعي غير مفعّلة (الوضع المجاني: مقارنة آلية + فحص HTML).", "note")

    st.markdown(theme.result_card(score, color, label, BRANDS[brand], items),
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.image(base64.b64decode(r["shot"]), caption="الصفحة المفحوصة",
             use_container_width=True)
    c2.image(base64.b64decode(r["ref"]), caption=f"الصفحة الرسمية ({BRANDS[brand]})",
             use_container_width=True)

theme.footer()