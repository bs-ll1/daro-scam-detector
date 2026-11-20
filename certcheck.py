from datetime import datetime, timezone

import requests


def cert_info(domain: str):
    data = None
    for _ in range(2):
        try:
            r = requests.get("https://crt.sh/",
                             params={"q": domain, "output": "json"},
                             timeout=20,
                             headers={"User-Agent": "daro-hackathon"})
            if r.status_code == 200:
                data = r.json()
                break
        except Exception:
            pass
    if data is None:
        return {"ok": False, "error": "تعذّر الاتصال بخدمة crt.sh (قد تكون مشغولة)"}

    def parse(s):
        return datetime.fromisoformat(s.split(".")[0]).replace(tzinfo=timezone.utc)

    dates = []
    for c in data:
        try:
            dates.append((parse(c["not_before"]), c))
        except Exception:
            pass
    if not dates:
        return {"ok": True, "count": 0}

    dates.sort(key=lambda x: x[0])
    first, fc = dates[0]
    hours = (datetime.now(timezone.utc) - first).total_seconds() / 3600
    return {"ok": True, "count": len(data),
            "first_issued": first.strftime("%Y-%m-%d %H:%M UTC"),
            "age_hours": hours, "issuer": fc.get("issuer_name", "")}


def describe_age(hours: float) -> str:
    if hours < 48:
        return f"{max(1, int(hours))} ساعة"
    return f"{int(hours // 24)} يوم"


def level(hours: float):
    if hours < 72:
        return "high"
    if hours < 24 * 30:
        return "medium"
    return None