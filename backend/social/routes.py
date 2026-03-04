"""Social Media Routes - Placeholder"""
from fastapi import APIRouter, Depends
from auth.utils import get_current_user, TokenData

router = APIRouter(prefix="/api/v1/social", tags=["Social"])

db = None

def set_database(database):
    global db
    db = database

@router.get("/accounts")
async def get_accounts(current_user: TokenData = Depends(get_current_user)):
    """Get social media accounts"""
    return {
        "status": "success",
        "data": [],
        "message": "Social media feature coming soon"
    }
