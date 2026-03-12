import re
from typing import Any, Dict, Optional

from services.customer_service import CustomerService


def _norm(text: str) -> str:
    return (text or "").strip()


def _norm_lower(text: str) -> str:
    return _norm(text).lower()


def _extract_after(text: str, patterns):
    for pat in patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            return (m.group(1) or "").strip(" ,.-")
    return ""


def _extract_number(text: str, patterns):
    for pat in patterns:
        m = re.search(pat, text, flags=re.I)
        if m:
            raw = (m.group(1) or "").strip()
            if raw.isdigit():
                return int(raw)
    return None


def _parse_customer_create_message(message: str) -> Dict[str, Any]:
    text = _norm(message)

    name = _extract_after(text, [
        r"(?:nama pelanggan|pelanggan baru nama|pelanggan nama|nama)\s+([^,\n]+)",
    ])

    phone = _extract_after(text, [
        r"(?:nomor|no hp|no tlpn|telepon|tlpn|hp)\s+([0-9+\-\s]{6,})",
    ]).replace(" ", "")

    store_name = _extract_after(text, [
        r"(?:nama toko|toko)\s+([^,\n]+)",
    ])

    address = _extract_after(text, [
        r"(?:alamat)\s+([^,\n]+)",
    ])

    customer_type = _extract_after(text, [
        r"(?:tipe|jenis|kategori)\s+([^,\n]+)",
    ])

    notes = _extract_after(text, [
        r"(?:catatan)\s+([^,\n]+)",
    ])

    if not customer_type:
        lower = text.lower()
        if "reseller" in lower:
            customer_type = "reseller"
        elif "toko baru" in lower:
            customer_type = "toko baru"

    extra: Dict[str, Any] = {}

    next_visit = _extract_after(text, [
        r"(?:kunjungan berikutnya|visit berikutnya|next visit)\s+([^,\n]+)",
    ])
    if next_visit:
        extra["next_visit_date"] = next_visit

    consignment_qty = _extract_number(text, [
        r"(?:jumlah barang yang dititipkan|barang titip|titip barang|titip)\s+(\d+)",
    ])
    if consignment_qty is not None:
        extra["consignment_qty"] = consignment_qty

    today_sales = _extract_number(text, [
        r"(?:penjualan hari ini|sales hari ini|terjual hari ini)\s+(\d+)",
    ])
    if today_sales is not None:
        extra["today_sales"] = today_sales

    owner_name = _extract_after(text, [
        r"(?:nama owner|owner|pemilik)\s+([^,\n]+)",
    ])
    if owner_name:
        extra["owner_name"] = owner_name

    payload = {
        "name": name,
        "phone": phone,
        "store_name": store_name,
        "address": address,
        "customer_type": customer_type,
        "notes": notes,
        "extra": extra,
    }
    return payload


def detect_customer_intent(message: str) -> Optional[Dict[str, Any]]:
    msg = _norm_lower(message)
    if not msg:
        return None

    if (
        ("simpan" in msg or "catat" in msg or "buat" in msg)
        and ("pelanggan" in msg or "customer" in msg)
    ):
        return {
            "intent": "buat_draft_customer",
            "payload": _parse_customer_create_message(message),
        }

    if any(x in msg for x in ["lihat draft", "draft terakhir", "tampilkan draft", "cek draft"]):
        return {"intent": "lihat_draft_terakhir"}

    if any(x in msg for x in ["konfirmasi draft", "lanjut simpan", "ya simpan", "ya lanjut", "simpan draft"]):
        m = re.search(r"\b(?:draft\s*)?(\d+)\b", msg)
        draft_id = int(m.group(1)) if m else None
        return {"intent": "konfirmasi_draft", "draft_id": draft_id}

    if any(x in msg for x in ["batalkan draft", "batal draft", "jangan simpan", "tidak jadi simpan", "tidak jadi"]):
        m = re.search(r"\b(?:draft\s*)?(\d+)\b", msg)
        draft_id = int(m.group(1)) if m else None
        return {"intent": "batalkan_draft", "draft_id": draft_id}

    if any(x in msg for x in ["lihat customer", "lihat pelanggan", "tampilkan customer", "tampilkan pelanggan", "cari customer", "cari pelanggan"]):
        m = re.search(r"\b(?:customer|pelanggan)\s+(\d+)\b", msg)
        customer_id = int(m.group(1)) if m else None

        q = ""
        if not customer_id:
            for key in ["lihat customer", "lihat pelanggan", "tampilkan customer", "tampilkan pelanggan", "cari customer", "cari pelanggan"]:
                if key in msg:
                    q = msg.split(key, 1)[1].strip()
                    break

        return {"intent": "lihat_customer", "customer_id": customer_id, "q": q}

    return None


async def execute_customer_intent(
    user_id: str,
    message: str,
    service: CustomerService,
) -> Dict[str, Any]:
    parsed = detect_customer_intent(message)
    if not parsed:
        return {
            "matched": False,
            "message": "Intent customer tidak dikenali",
        }

    intent = parsed["intent"]

    if intent == "buat_draft_customer":
        payload = parsed.get("payload") or {}
        if not (payload.get("name") or "").strip():
            return {
                "matched": True,
                "intent": intent,
                "message": "Nama pelanggan belum terbaca. Format yang aman: simpan pelanggan baru nama Budi, nomor 08123456789, nama toko Toko Budi Jaya",
                "data": payload,
            }

        draft = await service.prepare_customer_create(
            user_id=user_id,
            data=payload,
        )
        return {
            "matched": True,
            "intent": intent,
            "message": draft["summary_text"],
            "data": draft,
            "needs_confirmation": True,
        }

    if intent == "lihat_draft_terakhir":
        draft = await service.get_latest_pending_draft(user_id=user_id)
        if not draft:
            return {
                "matched": True,
                "intent": intent,
                "message": "Tidak ada draft pending.",
                "data": None,
            }
        return {
            "matched": True,
            "intent": intent,
            "message": draft["summary_text"],
            "data": draft,
        }

    if intent == "konfirmasi_draft":
        draft_id = parsed.get("draft_id")
        if draft_id is None:
            latest = await service.get_latest_pending_draft(user_id=user_id)
            if not latest:
                return {
                    "matched": True,
                    "intent": intent,
                    "message": "Tidak ada draft pending untuk dikonfirmasi.",
                    "data": None,
                }
            draft_id = latest["id"]

        result = await service.confirm_draft(draft_id=draft_id, user_id=user_id)
        saved = result["saved"]
        return {
            "matched": True,
            "intent": intent,
            "message": f"Draft {draft_id} berhasil disimpan untuk pelanggan {saved['name']}.",
            "data": result,
        }

    if intent == "batalkan_draft":
        draft_id = parsed.get("draft_id")
        if draft_id is None:
            latest = await service.get_latest_pending_draft(user_id=user_id)
            if not latest:
                return {
                    "matched": True,
                    "intent": intent,
                    "message": "Tidak ada draft pending untuk dibatalkan.",
                    "data": None,
                }
            draft_id = latest["id"]

        result = await service.cancel_draft(draft_id=draft_id, user_id=user_id)
        return {
            "matched": True,
            "intent": intent,
            "message": f"Draft {draft_id} dibatalkan.",
            "data": result,
        }

    if intent == "lihat_customer":
        customer_id = parsed.get("customer_id")
        q = (parsed.get("q") or "").strip()

        if customer_id is not None:
            item = await service.get_customer(customer_id=customer_id, user_id=user_id)
            if not item:
                return {
                    "matched": True,
                    "intent": intent,
                    "message": f"Customer dengan id {customer_id} tidak ditemukan.",
                    "data": None,
                }
            return {
                "matched": True,
                "intent": intent,
                "message": f"Data customer {item['name']} ditemukan.",
                "data": item,
            }

        rows = await service.list_customers(user_id=user_id, q=q, limit=10)
        if not rows:
            return {
                "matched": True,
                "intent": intent,
                "message": "Data customer tidak ditemukan.",
                "data": [],
            }

        if len(rows) == 1:
            item = rows[0]
            return {
                "matched": True,
                "intent": intent,
                "message": f"Data customer {item['name']} ditemukan.",
                "data": item,
            }

        names = ", ".join([r["name"] for r in rows[:5]])
        return {
            "matched": True,
            "intent": intent,
            "message": f"Ditemukan {len(rows)} customer. Contoh: {names}",
            "data": rows,
        }

    return {
        "matched": False,
        "message": "Intent belum didukung",
    }
