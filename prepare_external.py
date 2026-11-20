import csv
import random
import sys
from urllib.parse import urlparse

mode, path, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
random.seed(42)
domains = []

with open(path, encoding="utf-8", errors="ignore") as f:
    text = f.read().splitlines()

if mode == "phish":
    # OpenPhish: رابط في كل سطر. PhishTank CSV: عمود url
    if text and "url" in text[0].lower().split(","):
        idx = text[0].lower().split(",").index("url")
        urls = [row[idx] for row in csv.reader(text[1:]) if len(row) > idx]
    else:
        urls = [t.strip() for t in text if t.strip()]
    for u in urls:
        h = urlparse(u if "://" in u else "http://" + u).hostname
        if h:
            domains.append(h)
    label, source = "phish", sys.argv[4] if len(sys.argv) > 4 else "phishtank"
else:
    # Tranco: rank,domain
    for t in text[:2000]:
        parts = t.split(",")
        if len(parts) >= 2:
            domains.append(parts[1].strip())
    label, source = "legit", "tranco"

domains = sorted(set(domains))
random.shuffle(domains)
with open("benchmark_data.csv", "a", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    for d in domains[:n]:
        w.writerow([d, label, source, "global"])
print("أضيف", min(n, len(domains)), "نطاق")