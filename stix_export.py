import json
import uuid
from datetime import datetime, timezone


def _ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _id(kind):
    return f"{kind}--{uuid.uuid4()}"


def build_stix(r, brand=None, cert=None):
    now = _ts()
    score = r["risk_score"]
    itype = "malicious-activity" if score >= 75 else "anomalous-activity"
    objs = []

    def indicator(name, pattern):
        obj = {"type": "indicator", "spec_version": "2.1", "id": _id("indicator"),
               "created": now, "modified": now, "name": name,
               "indicator_types": [itype], "pattern": pattern,
               "pattern_type": "stix", "valid_from": now,
               "confidence": int(score), "labels": ["phishing", "impersonation"],
               "x_daro_risk_score": score, "x_daro_reasons": r["reasons"]}
        if cert and cert.get("first_issued"):
            obj["x_daro_first_cert_issued"] = cert["first_issued"]
        objs.append(obj)
        return obj

    dom = indicator(f"Suspicious domain {r['domain']}",
                    f"[domain-name:value = '{r['domain']}']")
    ip = None
    if r.get("ip"):
        ip = indicator(f"Server IP {r['ip']}", f"[ipv4-addr:value = '{r['ip']}']")

    if brand:
        ident = {"type": "identity", "spec_version": "2.1", "id": _id("identity"),
                 "created": now, "modified": now, "name": brand,
                 "identity_class": "organization"}
        objs.append(ident)
        objs.append({"type": "relationship", "spec_version": "2.1",
                     "id": _id("relationship"), "created": now, "modified": now,
                     "relationship_type": "related-to",
                     "source_ref": dom["id"], "target_ref": ident["id"],
                     "description": "Domain appears to impersonate this entity"})
    if ip:
        objs.append({"type": "relationship", "spec_version": "2.1",
                     "id": _id("relationship"), "created": now, "modified": now,
                     "relationship_type": "related-to",
                     "source_ref": dom["id"], "target_ref": ip["id"]})

    return json.dumps({"type": "bundle", "id": _id("bundle"), "objects": objs},
                      ensure_ascii=False, indent=2)


def build_simple(r, brand=None, cert=None):
    iocs = [{"type": "domain", "value": r["domain"]}]
    if r.get("ip"):
        iocs.append({"type": "ipv4", "value": r["ip"]})
    return json.dumps({
        "tool": "Daro (hackathon prototype)",
        "generated_at": _ts(),
        "risk_score": r["risk_score"],
        "impersonated_entity": brand,
        "first_cert_issued": (cert or {}).get("first_issued"),
        "indicators": iocs,
        "reasons": r["reasons"],
        "note": "Automated preliminary analysis. Requires human review.",
    }, ensure_ascii=False, indent=2)