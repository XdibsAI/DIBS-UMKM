import re

def classify_note(text: str):
    lower = (text or "").lower().strip()

    category = "general"

    if re.search(r'\brp\b|harga|beli|bayar|utang|modal|pengeluaran|pemasukan', lower):
        category = "finance"
    elif re.search(r'besok|hari ini|jam\s*\d+|meeting|rapat|jadwal|schedule|nanti', lower):
        category = "schedule"
    elif re.search(r'error|bug|server|build|deploy|printer|api|database|flutter|backend', lower):
        category = "technical"
    elif re.search(r'bahan|resep|produksi|stok bahan|masak', lower):
        category = "production"
    elif re.search(r'promosi|video|caption|posting|jualan|konten', lower):
        category = "marketing"

    amounts = re.findall(r'rp\s*([\d\.\,]+)', lower)
    total_money = 0
    for amt in amounts:
        try:
            total_money += int(amt.replace('.', '').replace(',', ''))
        except:
            pass

    return {
        "category": category,
        "money_total": total_money,
    }
