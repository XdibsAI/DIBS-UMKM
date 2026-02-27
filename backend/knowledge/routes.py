"""Knowledge Routes"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
import logging
import io
from pydantic import BaseModel

from auth.utils import get_current_user, TokenData

router = APIRouter(prefix="/api/v1/knowledge", tags=["Knowledge"])
logger = logging.getLogger('DIBS1')

db = None

def set_database(database):
    global db
    db = database

# TAMBAH: Model untuk request report
class ReportRequest(BaseModel):
    period: str
    start_date: str = None
    end_date: str = None

@router.get("")
async def get_knowledge(current_user: TokenData = Depends(get_current_user)):
    """Get user's knowledge entries"""
    try:
        entries = await db.fetch_all(
            "SELECT * FROM knowledge WHERE user_id = ? ORDER BY created_at DESC",
            (current_user.user_id,)
        )
        return {"status": "success", "data": [dict(e) for e in entries]}
    except Exception as e:
        logger.error(f"Get knowledge error: {e}")
        raise HTTPException(500, str(e))

@router.post("/report")
async def generate_report(
    request: ReportRequest,  # UBAH: menggunakan model
    current_user: TokenData = Depends(get_current_user)
):
    """Generate knowledge report"""
    try:
        now = datetime.now()
        
        # UBAH: menggunakan request.period, request.start_date, request.end_date
        if request.period == "today":
            start = now.replace(hour=0, minute=0, second=0)
        elif request.period == "week":
            start = now - timedelta(days=7)
        elif request.period == "month":
            start = now - timedelta(days=30)
        else:
            start = datetime.fromisoformat(request.start_date) if request.start_date else now - timedelta(days=30)

        end = datetime.fromisoformat(request.end_date) if request.end_date else now

        entries = await db.fetch_all(
            "SELECT * FROM knowledge WHERE user_id = ? AND created_at BETWEEN ? AND ? ORDER BY created_at",
            (current_user.user_id, start.isoformat(), end.isoformat())
        )

        by_category = {}
        total_finance = 0

        for entry in entries:
            cat = entry['category'] or 'general'
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(dict(entry))

            if cat == 'finance' and entry['content']:
                import re
                amounts = re.findall(r'Rp\s*([\d.,]+)', entry['content'])
                for amt in amounts:
                    try:
                        total_finance += float(amt.replace('.', '').replace(',', ''))
                    except:
                        pass

        report_lines = [
            f"# LAPORAN {request.period.upper()}",  # UBAH: menggunakan request.period
            f"Periode: {start.strftime('%Y-%m-%d')} s/d {end.strftime('%Y-%m-%d')}",
            f"Total Entries: {len(entries)}",
            "",
        ]

        if total_finance > 0:
            report_lines.extend([
                "## 💰 RINGKASAN KEUANGAN",
                f"Total Pengeluaran: Rp {total_finance:,.0f}",
                ""
            ])

        for cat, items in by_category.items():
            report_lines.append(f"## 📂 {cat.upper()} ({len(items)} entries)")
            for item in items[:10]:
                report_lines.append(f"- {item['content'][:100]}...")
            report_lines.append("")

        report_text = "\n".join(report_lines)

        return {
            "status": "success",
            "data": {
                "title": f"Laporan {request.period.capitalize()}",  # UBAH: menggunakan request.period
                "report": report_text,
                "stats": {
                    "total_entries": len(entries),
                    "total_finance": total_finance,
                    "categories": list(by_category.keys())
                }
            }
        }
    except Exception as e:
        logger.error(f"Generate report error: {e}")
        raise HTTPException(500, str(e))

@router.post("/report/pdf")
async def download_pdf(
    request: ReportRequest,  # UBAH: menggunakan model
    current_user: TokenData = Depends(get_current_user)
):
    """Generate PDF report"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        # UBAH: panggil generate_report dengan request
        report_data = await generate_report(request, current_user)
        report_text = report_data['data']['report']

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        for line in report_text.split('\n'):
            if line.startswith('# '):
                story.append(Paragraph(line[2:], styles['Title']))
            elif line.startswith('## '):
                story.append(Paragraph(line[3:], styles['Heading2']))
            elif line:
                story.append(Paragraph(line, styles['Normal']))
            story.append(Spacer(1, 12))

        doc.build(story)
        buffer.seek(0)

        filename = f"laporan_{request.period}_{datetime.now().strftime('%Y%m%d')}.pdf"  # UBAH: menggunakan request.period

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise HTTPException(500, str(e))
