from fastapi import APIRouter, HTTPException, Request
from schemas.voucher_schema import VoucherCreate, VoucherRead, VoucherUpdate
from controllers.voucher_controller import create_voucher, get_voucher, get_vouchers, update_voucher
from enums import Role
router = APIRouter()

@router.post("/vouchers/", response_model=VoucherRead)
async def create_voucher_endpoint(voucher: VoucherCreate, request: Request):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    voucher_data = voucher.dict()
    try:
        new_voucher = await create_voucher(voucher_data)
        return new_voucher
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/vouchers/", response_model=dict)
async def get_vouchers_endpoint(page: int = 1, limit: int = 10):
    vouchers = await get_vouchers(page, limit)
    return vouchers

@router.get("/vouchers/{voucher_id}", response_model=VoucherRead)
async def get_voucher_by_id_endpoint(voucher_id: int):
    voucher = await get_voucher(voucher_id)
    if voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher

@router.patch("/vouchers/{voucher_id}", response_model=VoucherRead)
async def update_voucher_endpoint(voucher_id: int, voucher: VoucherUpdate, request: Request):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    voucher_data = voucher.dict()
    updated_voucher = await update_voucher(voucher_id, voucher_data)
    if updated_voucher is None:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return updated_voucher