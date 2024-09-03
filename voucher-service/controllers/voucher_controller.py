from models.voucher import Voucher
from datetime import datetime
from models.mongo import engine
from fastapi import HTTPException

async def create_voucher(voucher_data: dict) -> Voucher:
    next_voucher_id = await get_next_voucher_id()
    voucher_data["id"] = next_voucher_id
    voucher = Voucher(**voucher_data)
    await engine.save(voucher)
    return voucher

async def get_voucher(voucher_id: int) -> Voucher:
    voucher = await engine.find_one(Voucher, Voucher.id == voucher_id)
    return voucher

async def get_vouchers(page: int = 1, limit: int = 10) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    vouchers = await engine.find(Voucher, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/vouchers/?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/vouchers/?page={page + 1}&limit={limit}' if len(vouchers) == limit else None
    
    total = await engine.count(Voucher)
    total_pages = total // limit + 1 if total % limit else total // limit
    
    res = {
        "data": [voucher.dict() for voucher in vouchers],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res

async def update_voucher(voucher_id: int, voucher_data: dict) -> Voucher:
    voucher = await engine.find_one(Voucher, Voucher.id == voucher_id)
    if not voucher:
        return None
    for key, value in voucher_data.items():
        if hasattr(voucher, key) and value is not None:
            setattr(voucher, key, value)
    voucher.updated_at = datetime.utcnow()
    await engine.save(voucher)
    return voucher

async def get_next_voucher_id() -> int:
    last_voucher = await engine.find_one(Voucher, sort=Voucher.id.desc())
    return last_voucher.id + 1 if last_voucher else 1