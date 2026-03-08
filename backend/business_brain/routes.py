from fastapi import APIRouter, HTTPException, Depends, Query
import logging
from datetime import datetime

from auth.utils import get_current_user, TokenData
from .memory_engine import classify_note
from .retail_intelligence import (
    get_low_stock_products,
    get_sales_rows,
    aggregate_top_products,
    summarize_payment_methods,
    total_sales,
)
from .recommendation_engine import build_recommendations

router = APIRouter(prefix="/api/v1/business-brain", tags=["Business Brain"])
logger = logging.getLogger("DIBS1")
db = None


def set_database(database):
    global db
    db = database


@router.post("/classify-note")
async def classify_note_route(
    data: dict,
    current_user: TokenData = Depends(get_current_user),
):
    try:
        text = str(data.get("text", "")).strip()
        if not text:
            raise HTTPException(400, "Text wajib diisi")

        result = classify_note(text)
        return {"status": "success", "data": result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"classify note error: {e}")
        raise HTTPException(500, str(e))


@router.get("/sales-insight")
async def sales_insight(
    period: str = Query(default="today"),
    current_user: TokenData = Depends(get_current_user),
):
    try:
        user_id = str(getattr(current_user, "user_id", getattr(current_user, "id", "")))
        sales_rows, start, end = await get_sales_rows(db, user_id, period=period)

        data = {
            "period": period,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "total_sales": total_sales(sales_rows),
            "total_transactions": len(sales_rows),
            "top_products": aggregate_top_products(sales_rows),
            "payment_methods": summarize_payment_methods(sales_rows),
        }
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"sales insight error: {e}")
        raise HTTPException(500, str(e))


@router.get("/daily-summary")
async def daily_summary(current_user: TokenData = Depends(get_current_user)):
    try:
        user_id = str(getattr(current_user, "user_id", getattr(current_user, "id", "")))

        sales_rows, start, end = await get_sales_rows(db, user_id, period="today")
        week_sales_rows, _, _ = await get_sales_rows(db, user_id, period="week")
        low_stock = await get_low_stock_products(db, user_id, threshold=5)

        notes = await db.fetch_all(
            """
            SELECT id, content, category, created_at
            FROM knowledge
            WHERE user_id = ? AND created_at BETWEEN ? AND ?
            ORDER BY created_at DESC
            """,
            (user_id, start.isoformat(), end.isoformat())
        )

        finance_total = 0
        finance_notes = []

        for row in notes:
            item = dict(row)
            if item.get("category") == "finance":
                finance_notes.append(item)
                classified = classify_note(item.get("content", ""))
                finance_total += int(classified.get("money_total", 0) or 0)

        sales_total = total_sales(sales_rows)
        profit_today = sales_total - finance_total

        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_sales": sales_total,
            "total_transactions": len(sales_rows),
            "top_products": aggregate_top_products(sales_rows),
            "top_products_week": aggregate_top_products(week_sales_rows),
            "low_stock_products": low_stock,
            "finance_notes_total": finance_total,
            "finance_notes_count": len(finance_notes),
            "profit_today": profit_today,
            "payment_methods": summarize_payment_methods(sales_rows),
        }
        summary["recommendations"] = build_recommendations(summary)

        return {"status": "success", "data": summary}
    except Exception as e:
        logger.error(f"daily summary error: {e}")
        raise HTTPException(500, str(e))
