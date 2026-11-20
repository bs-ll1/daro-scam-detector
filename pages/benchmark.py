import hashlib
from pathlib import Path

import pandas as pd
import streamlit as st

import theme

theme.setup("القياس", "benchmark")
C = theme.COLORS

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "benchmark_data.csv"


@st.cache_resource
def load_engine():
    import main
    main.record = lambda *a, **k: None   # القياس لا يلوّث قاعدة الحملات
    main.resolve_ip = lambda d: None     # ولا يتصل بالنطاقات المفحوصة
    return main


def metrics(rows, thr):
    tp = fp = tn = fn = 0
    for r in rows:
        pred = (not r["official"]) and r["score"] >= thr
        actual = r["label"] == "phish"
        if pred and actual:
            tp += 1
        elif pred:
            fp += 1
        elif actual:
            fn += 1
        else:
            tn += 1
    n = tp + fp + tn + fn
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None
    f1 = (2 * prec * rec / (prec + rec)) if prec and rec else None
    acc = (tp + tn) / n if n else None
    return {"n": n, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": prec, "recall": rec, "f1": f1, "accuracy": acc}


def pct(x):
    return "—" if x is None else f"{x * 100:.0f}%"


def is_test(url):
    return int(hashlib.md5(str(url).encode()).hexdigest(), 16) % 2 == 1


def run_engine(fn, df, label):
    rows = []
    prog = st.progress(0.0, text=label)
    for i, (_, r) in enumerate(df.iterrows(), 1):
        res = fn(str(r["url"]), use_ai=False)
        rows.append({"url": r["url"], "domain": res["domain"], "label": r["label"],
                     "source": r["source"], "scope": r["scope"],
                     "score": res["risk_score"], "official": bool(res.get("official")),
                     "reasons": "؛ ".join(res["reasons"])})
        prog.progress(i / len(df), text=label)
    prog.empty()
    return rows


theme.hero("قياس", "الأداء", "نختبر المحرك على روابط معروفة الحقيقة ونقارن قبل وبعد التحسين بصدق")

up = st.file_uploader("ملف بيانات آخر (اختياري، أعمدة: url,label,source,scope)", type="csv")
if up is not None:
    df = pd.read_csv(up)
elif DATA.exists():
    df = pd.read_csv(DATA)
else:
    st.error("ملف benchmark_data.csv غير موجود في مجلد المشروع.")
    st.stop()

if "url" not in df.columns or "label" not in df.columns:
    st.error("الملف لازم يحتوي عمودي url و label.")
    st.stop()
for col in ("source", "scope"):
    if col not in df.columns:
        df[col] = "unknown"
df["label"] = df["label"].astype(str).str.strip().str.lower()
df = df[df["label"].isin(["phish", "legit"])].drop_duplicates("url")

st.caption(f"حجم العيّنة: {len(df)} رابط "
           f"({(df.label == 'phish').sum()} احتيالي، {(df.label == 'legit').sum()} سليم). "
           "القياس بالقواعد فقط: بدون ذكاء اصطناعي وبدون أي اتصال بالنطاقات المفحوصة.")

if st.button("شغّل القياس (قبل وبعد التحسين)"):
    eng = load_engine()
    if not hasattr(eng, "analyze_domain_original"):
        st.error("المحرك المحسّن غير مفعّل: تأكد أن آخر سطر في main.py هو import improve ثم أعد تشغيل Streamlit.")
        st.stop()
    st.session_state["base"] = run_engine(eng.analyze_domain_original, df, "المحرك الأساسي...")
    st.session_state["new"] = run_engine(eng.analyze_domain_v2 if hasattr(eng, "analyze_domain_v2")
                                         else eng.analyze_domain, df, "المحرك المحسّن...")

base, new = st.session_state.get("base"), st.session_state.get("new")
if base and new:
    thr = st.slider("عتبة الحكم (فوقها نعتبر الرابط احتيالياً)", 10, 100, 50)

    subsets = {
        "الكل": lambda r: True,
        "نصف الاختبار (تقسيم ثابت بالهاش)": lambda r: is_test(r["url"]),
        "المصادر الخارجية فقط (بدون المصطنع)": lambda r: r["source"] != "synthetic",
        "تصيّد إماراتي (مصطنع) + سليم إماراتي": lambda r: r["scope"] == "uae",
        "تصيّد عالمي + سليم عالمي": lambda r: r["scope"] == "global",
    }

    st.markdown('<div class="sec">مقارنة قبل / بعد التحسين</div>', unsafe_allow_html=True)
    table = []
    for name, fn in subsets.items():
        b = metrics([r for r in base if fn(r)], thr)
        a = metrics([r for r in new if fn(r)], thr)
        if not a["n"]:
            continue
        table.append({"المجموعة": name, "العدد": a["n"],
                      "Precision قبل": pct(b["precision"]), "Precision بعد": pct(a["precision"]),
                      "Recall قبل": pct(b["recall"]), "Recall بعد": pct(a["recall"]),
                      "F1 قبل": pct(b["f1"]), "F1 بعد": pct(a["f1"])})
    st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
    st.caption("تنبيه علمي: رأينا أخطاء القياس الأول على كل البيانات قبل التحسين، فنصف الاختبار ليس مستقلاً تماماً. "
               "الاختبار الأنظف: حمّل تصيّداً جديداً لاحقاً (مصدر openphish_holdout) وقس عليه فقط. "
               "كما أن المواقع السليمة الشائعة تُستثنى عمداً بقائمة المواقع الشائعة.")

    which = st.radio("اعرض التفاصيل للمحرك:", ["بعد التحسين", "قبل التحسين"], horizontal=True)
    rows = new if which == "بعد التحسين" else base
    m = metrics(rows, thr)
    st.markdown(f"""<div class="stats4">
<div class="stat"><b style="color:{C['ok']}">{pct(m['precision'])}</b><span>الدقة (Precision)</span></div>
<div class="stat"><b style="color:{C['info']}">{pct(m['recall'])}</b><span>الاستدعاء (Recall)</span></div>
<div class="stat"><b style="color:{C['warn']}">{pct(m['f1'])}</b><span>F1</span></div>
<div class="stat"><b>{pct(m['accuracy'])}</b><span>الدقة الكلية</span></div>
</div>""", unsafe_allow_html=True)

    st.markdown(f"""<table class="tbl"><tr><th></th><th>النظام: مشبوه</th><th>النظام: سليم</th></tr>
<tr><td>الحقيقة: احتيالي</td><td style="color:{C['ok']}">{m['tp']} (اكتُشف)</td>
<td style="color:{C['bad']}">{m['fn']} (فات)</td></tr>
<tr><td>الحقيقة: سليم</td><td style="color:{C['bad']}">{m['fp']} (إنذار كاذب)</td>
<td style="color:{C['ok']}">{m['tn']} (عدّى صح)</td></tr></table>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">أخطاء النظام (نقاط الضعف)</div>', unsafe_allow_html=True)
    wrong = [r for r in rows if ((not r["official"]) and r["score"] >= thr) != (r["label"] == "phish")]
    if wrong:
        st.dataframe(pd.DataFrame([{
            "النوع": "إنذار كاذب" if r["label"] == "legit" else "احتيال فات",
            "النطاق": r["domain"], "الدرجة": r["score"], "المصدر": r["source"],
            "الأسباب": r["reasons"] or "لا توجد إشارات"} for r in wrong]),
            use_container_width=True, hide_index=True)
    else:
        st.success("لا أخطاء على هذه العيّنة، وغالباً العيّنة سهلة. أضف بيانات خارجية.")

    st.download_button("تحميل النتائج (CSV)",
                       data=pd.DataFrame(rows).to_csv(index=False).encode("utf-8-sig"),
                       file_name="daro_benchmark_results.csv", mime="text/csv")

theme.footer()