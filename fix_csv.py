import csv

rows = []
with open("benchmark_data.csv", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# نفصل أي سطر انلصق مع غيره
for line in text.replace("\r", "").split("\n"):
    line = line.strip()
    if not line or line.startswith("url,label"):
        continue
    parts = line.split(",")
    # كل 4 حقول = سجل واحد
    for i in range(0, len(parts) - 3, 4):
        url, label, source, scope = [p.strip() for p in parts[i:i + 4]]
        if label in ("phish", "legit") and url:
            rows.append((url, label, source, scope))

seen, clean = set(), []
for r in rows:
    if r[0] not in seen:
        seen.add(r[0])
        clean.append(r)

with open("benchmark_data.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["url", "label", "source", "scope"])
    w.writerows(clean)

print("تم. عدد السجلات:", len(clean),
      "| احتيالي:", sum(r[1] == "phish" for r in clean),
      "| سليم:", sum(r[1] == "legit" for r in clean))