import html
from datetime import datetime

import requests
import streamlit as st

import theme

theme.setup("فاحص الرسائل", "messages")

API = "http://127.0.0.1:8000/check-message"
C = theme.COLORS

theme.hero("فحص الرسائل", "المشبوهة", "ألصق رسالة SMS أو واتساب، ونحلل النص والروابط معاً")

EXAMPLES = {
    "مخالفة مرورية": "عاجل: تم تسجيل مخالفة مرورية على مركبتك. يرجى سداد الرسوم فوراً خلال 24 ساعة لتجنب الايقاف. اضغط هنا https://salik-fine-pay.xyz",
    "طلب رمز التحقق": "مصرف الامارات: تم تعليق حسابك. لإعادة التفعيل ارسل رمز التحقق OTP الذي وصلك وبيانات البطاقة عبر واتساب.",
    "رسالة سليمة": "عزيزي العميل، تم تجديد اشتراكك بنجاح. للتفاصيل زر موقعنا https://www.du.ae",
}

run = False
st.caption("جرّب رسالة جاهزة:")
cols = st.columns(3)
for c, (name, body) in zip(cols, EXAMPLES.items()):
    if c.button(name, key=name):
        st.session_state["msg"] = body
        run = True

text = st.text_area("نص الرسالة", key="msg", height=140, placeholder="الصق الرسالة هنا...")
if st.button("افحص الرسالة"):
    run = True

if run and text.strip():
    try:
        with st.spinner("جاري تحليل الرسالة..."):
            r = requests.post(API, json={"text": text}, timeout=60).json()
    except requests.exceptions.ConnectionError:
        st.error("السيرفر مو شغّال. شغّل uvicorn في التيرمنال الأول.")
        st.stop()

    score = r["risk_score"]
    if r["official_only"] and score < 40:
        color, label = C["ok"], "الروابط رسمية ولا توجد مؤشرات قوية"
    elif score >= 70:
        color, label = C["bad"], "رسالة احتيالية على الأغلب"
    elif score >= 40:
        color, label = C["warn"], "رسالة مشبوهة: لا تضغط الرابط ولا ترسل بياناتك"
    else:
        color, label = C["info"], "لا توجد مؤشرات خطورة واضحة"

    items = "".join(theme.item(x) for x in r["reasons"])
    for f in r["flags"]:
        items += theme.item(f"{f['name']} ({'، '.join(f['matched'])})")
    ai = r.get("ai")
    if ai and "reason_ar" in ai:
        items += theme.item(f"تحليل الذكاء الاصطناعي: {ai['reason_ar']}", "ai")
    elif ai and "error" in ai:
        items += theme.item("تعذّر تحليل الذكاء الاصطناعي، النتيجة من الفحص الآلي فقط.", "note")
    else:
        items += theme.item("طبقة الذكاء الاصطناعي غير مفعّلة (الوضع المجاني: تحليل بالقواعد).", "note")

    st.markdown(theme.result_card(score, color, label, "تحليل النص + الروابط", items),
                unsafe_allow_html=True)

    if r["links"]:
        st.markdown("**الروابط المستخرجة من الرسالة:**")
        for l in r["links"]:
            if l["official"]:
                tag = "✅ رسمي"
            elif l["risk_score"] >= 50:
                tag = f'🚨 مشبوه ({l["risk_score"]}/100)'
            else:
                tag = f'❔ غير مصنّف ({l["risk_score"]}/100)'
            st.markdown(f'<div class="lnk">{html.escape(l["domain"])} — {tag}</div>',
                        unsafe_allow_html=True)
    else:
        st.caption("لا توجد روابط في الرسالة.")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = ["تقرير فحص رسالة | منصة درع", f"وقت الفحص: {now}",
             f"درجة الخطورة: {score}/100", f"التصنيف: {label}", "",
             "نص الرسالة:", text, "", "المؤشرات:"]
    lines += [f"  - {x}" for x in r["reasons"]]
    lines += [f"  - {f['name']}" for f in r["flags"]]
    lines += ["", "الروابط:"] + [f"  - {l['domain']} ({l['risk_score']}/100)" for l in r["links"]]
    lines += ["", "ملاحظة: تحليل آلي أولي ويحتاج مراجعة بشرية قبل أي بلاغ رسمي."]
    st.download_button("📄 توليد ملخص بلاغ", data="\n".join(lines).encode("utf-8-sig"),
                       file_name="daro_message_report.txt", mime="text/plain")
elif run:
    st.info("الصق نص الرسالة أولاً")

theme.footer()