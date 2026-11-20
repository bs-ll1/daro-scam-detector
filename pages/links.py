import re
import time
from datetime import datetime

import requests
import streamlit as st

import certcheck
import stix_export
import theme

theme.setup("فاحص الروابط", "links")

API = "http://127.0.0.1:8000/check-domain"
C = theme.COLORS

st.session_state.setdefault("hist", [])


@st.cache_data(ttl=600, show_spinner=False)
def get_cert(domain):
    return certcheck.cert_info(domain)


def build_report(r, label, link_input, cert_txt=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reasons = "\n".join(f"  - {x}" for x in r["reasons"]) or "  - لا توجد إشارات مرصودة"
    ai = r.get("ai")
    ai_txt = ""
    if ai and "reason_ar" in ai:
        ent = ai.get("impersonated_entity")
        ai_txt = f"\nتحليل الذكاء الاصطناعي: {ai['reason_ar']}"
        if ent and ent != "null":
            ai_txt += f"\nالجهة المنتحَلة المحتملة: {ent}"
    if cert_txt:
        ai_txt += f"\nشفافية الشهادات (crt.sh): {cert_txt}"
    return f"""==============================================
  تقرير فحص رابط | Link Analysis Report
  منصة درع (Daro) - للمراجعة والتحقق
==============================================

وقت الفحص (Scan time): {now}
الرابط المُدخل (Input): {link_input}
الدومين المستخرج (Domain): {r['domain']}

درجة الخطورة (Risk score): {r['risk_score']}/100
التصنيف (Verdict): {label}

الأسباب والإشارات (Indicators):
{reasons}{ai_txt}

----------------------------------------------
ملاحظة: هذا التقرير ناتج عن تحليل آلي أولي
(قواعد + مطابقة أسماء الجهات)، ولا يُعد دليلاً
قاطعاً. يُنصح بالتحقق اليدوي قبل رفع أي بلاغ
رسمي، ومنها: محتوى الصفحة وبيانات الاستضافة.
==============================================
"""


theme.hero("فحص الروابط", "الاحتيالية", "ألصق أي رابط أو دومين لتحليل انتحاله للجهات الرسمية")

run = False
st.caption("جرّب مثال سريع:")
examples = ["https://salik.ae.com", "dubaipolice.gov.ae", "uaepass.ae"]
cols = st.columns(3)
for c, ex in zip(cols, examples):
    if c.button(ex, key=ex):
        st.session_state["link"] = ex
        run = True

link = st.text_input("الرابط أو الدومين", key="link", placeholder="https://example.com")
if st.button("ابدأ التحليل"):
    run = True

STEPS = ["استخراج الدومين وتنظيف الرابط",
         "مطابقته مع الجهات الرسمية",
         "فحص الامتداد وأنماط الاحتيال",
         "حساب درجة الخطورة وكتابة التقرير"]

if run and link.strip():
    box = st.empty()
    for i in range(len(STEPS)):
        h = ""
        for j, s_ in enumerate(STEPS):
            if j < i:
                h += f'<div class="step done">✔ {s_}</div>'
            elif j == i:
                h += f'<div class="step now">◉ {s_}...</div>'
            else:
                h += f'<div class="step">○ {s_}</div>'
        box.markdown(f'<div class="scan">{h}</div>', unsafe_allow_html=True)
        time.sleep(0.35)

    try:
        r = requests.get(API, params={"domain": link}, timeout=40).json()
    except requests.exceptions.ConnectionError:
        box.empty()
        st.error("السيرفر مو شغّال. شغّل uvicorn في التيرمنال الأول.")
        st.stop()
    box.empty()

    score = r["risk_score"]
    if r.get("official"):
        color, label = C["ok"], "موقع رسمي موثوق"
    elif score >= 75:
        color, label = C["bad"], "رابط احتيالي مشتبه به"
    elif score >= 40:
        color, label = C["warn"], "يحتاج حذر"
    elif r.get("unknown"):
        color, label = C["unk"], "غير مصنّف: تحقق يدوياً قبل الدفع أو إدخال بياناتك"
    else:
        color, label = C["info"], "لا توجد مؤشرات خطورة واضحة"
    st.session_state.hist.insert(0, (r["domain"], score, label))

    items = "".join(theme.item(x) for x in r["reasons"])

    # فحص شفافية الشهادات (للنطاقات غير الرسمية فقط)
    cert, cert_txt = None, ""
    if not r.get("official"):
        with st.spinner("فحص سجلات شفافية الشهادات (crt.sh)..."):
            cert = get_cert(r["domain"])
        if cert.get("ok") and cert.get("count"):
            age = certcheck.describe_age(cert["age_hours"])
            cert_txt = f"أول شهادة SSL للنطاق صدرت قبل {age} ({cert['first_issued']})"
            lvl = certcheck.level(cert["age_hours"])
            if lvl == "high":
                items += theme.item("تحذير: " + cert_txt + ". نطاق حديث جداً، وهذا نمط شائع في الحملات الاحتيالية")
            elif lvl == "medium":
                items += theme.item("تنبيه: " + cert_txt)
            else:
                items += theme.item(cert_txt, "note")
        elif cert.get("ok"):
            items += theme.item("لا توجد شهادات مسجّلة لهذا النطاق في crt.sh", "note")
        else:
            items += theme.item(cert.get("error", "تعذّر فحص الشهادات"), "note")

    ai = r.get("ai")
    if ai and "reason_ar" in ai:
        ent = ai.get("impersonated_entity")
        ent_txt = f" | الجهة المنتحَلة: {ent}" if ent and ent != "null" else ""
        items += theme.item(f"تحليل الذكاء الاصطناعي: {ai['reason_ar']}{ent_txt}", "ai")
    elif ai and "error" in ai:
        items += theme.item("تعذّر تحليل الذكاء الاصطناعي، النتيجة من الفحص الآلي فقط.", "note")
    elif not r.get("official"):
        items += theme.item("طبقة الذكاء الاصطناعي غير مفعّلة (الوضع المجاني: تحليل بالقواعد).", "note")

    st.markdown(theme.result_card(score, color, label, r["domain"], items),
                unsafe_allow_html=True)

    report = build_report(r, label, link, cert_txt)
    st.download_button("📄 توليد ملخص بلاغ / دليل فني",
                       data=report.encode("utf-8-sig"),
                       file_name=f"daro_report_{r['domain']}.txt", mime="text/plain")

    # تصدير مؤشرات الاختراق (للروابط المشبوهة فقط)
    if not r.get("official") and score >= 50:
        brand = None
        for x in r["reasons"]:
            m = re.search(r"ينتحل شكل الجهة الرسمية \((.+?)\)", x)
            if m:
                brand = m.group(1)
        c1, c2 = st.columns(2)
        c1.download_button("🧾 تصدير IoC بصيغة STIX 2.1",
                           data=stix_export.build_stix(r, brand, cert).encode("utf-8"),
                           file_name=f"daro_{r['domain']}_stix21.json",
                           mime="application/json")
        c2.download_button("📦 تصدير IoC (JSON مبسّط)",
                           data=stix_export.build_simple(r, brand, cert).encode("utf-8"),
                           file_name=f"daro_{r['domain']}_ioc.json",
                           mime="application/json")
    elif not r.get("official"):
        st.caption("تصدير مؤشرات الاختراق متاح للروابط المشبوهة فقط (الدرجة 50 فأكثر).")

    with st.expander("معاينة التقرير / نسخ النص"):
        st.code(report, language=None)
elif run:
    st.info("اكتب رابط أولاً")

if st.session_state.hist:
    with st.expander("سجل الفحوصات"):
        for d, s_, l in st.session_state.hist[:10]:
            st.markdown(f"`{d}` — **{s_}/100** — {l}")

theme.footer()