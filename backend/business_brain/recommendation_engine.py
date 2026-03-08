def build_recommendations(summary: dict):
    recs = []

    total_sales = int(summary.get("total_sales", 0) or 0)
    finance_total = int(summary.get("finance_notes_total", 0) or 0)
    profit_today = int(summary.get("profit_today", total_sales - finance_total) or 0)

    for item in summary.get("low_stock_products", []):
        recs.append(f"Restock {item['name']} karena stok tinggal {item['stock']}")

    top_products = summary.get("top_products", [])
    if top_products:
        recs.append(f"Promosikan {top_products[0]['name']} karena paling laris")

    if finance_total > total_sales and total_sales > 0:
        recs.append("Pengeluaran hari ini lebih besar dari penjualan, cek biaya operasional")

    if total_sales == 0:
        recs.append("Belum ada penjualan hari ini, dorong promosi produk utama")

    if profit_today > 0:
        recs.append(f"Profit hari ini sekitar Rp {profit_today:,}".replace(",", "."))

    return recs[:5]
