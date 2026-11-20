from fastapi import APIRouter
from pydantic import BaseModel

import vision

router = APIRouter()


class VisualReq(BaseModel):
    url: str
    brand: str | None = None


@router.post("/visual-check")
def visual_check(req: VisualReq):
    import main
    domain = main.clean_domain(req.url)
    if main.is_official(domain):
        return {"ok": False, "error": "هذا دومين رسمي موثوق، لا يحتاج مقارنة"}
    brand = req.brand
    if not brand:
        guess, score = main.impersonation(domain)
        brand = guess if score >= 80 else None
    return vision.run(req.url, brand or "")