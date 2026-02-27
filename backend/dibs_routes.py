from fastapi import APIRouter
from bridge import dibs_engine

router = APIRouter(prefix="/dibs", tags=["Dibs Powerups"])

@router.post("/learn")
async def learn(text: str, category: str = "general"):
    """Instruksi [2026-01-06]: Simpan info ke database"""
    return {"message": dibs_engine.store_knowledge(text, category)}

@router.get("/ask")
async def ask(q: str):
    """Instruksi [2026-01-06]: Munculkan info dari database"""
    return {"response": dibs_engine.recall_knowledge(q)}

@router.get("/search")
async def search(query: str):
    """Cari di internet lewat Serper.dev"""
    return await dibs_engine.web_search(query)
