from controllers.voucher_exchange_controller import get_voucher_exchange, create_voucher_exchange, mark_voucher_exchange, get_voucher_exchanges, get_my_voucher_exchanges
from fastapi import APIRouter, HTTPException, Request
from schemas.voucher_exchange_schema import VoucherExchangeCreate, VoucherExchangeRead
from enums import Role

router = APIRouter()

@router.post("/voucher_exchanges/", response_model=VoucherExchangeRead)
async def create_voucher_exchange_endpoint(voucher_exchange: VoucherExchangeCreate, request: Request):
    try:
        voucher_exchange_data = voucher_exchange.dict()
        voucher_exchange_data["user_id"] = request.state.user.get("user_id")
        new_voucher_exchange = await create_voucher_exchange(voucher_exchange_data)
        return new_voucher_exchange
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/voucher_exchanges/", response_model=dict)
async def get_voucher_exchanges_endpoint(
    request: Request,
    page: int = 1,
    limit: int = 10
):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    return await get_voucher_exchanges(page, limit)

@router.get("/voucher_exchanges/me/", response_model=dict)
async def get_my_voucher_exchanges_endpoint(
    request: Request,
    page: int = 1,
    limit: int = 10
):
    return await get_my_voucher_exchanges(page, limit, request.state.user.get("user_id"))

@router.get("/voucher_exchanges/{voucher_exchange_id}/", response_model=VoucherExchangeRead)
async def get_voucher_exchange_endpoint(voucher_exchange_id: int):
    voucher_exchange = await get_voucher_exchange(voucher_exchange_id)
    if not voucher_exchange:
        raise HTTPException(status_code=404, detail="Voucher exchange not found")
    return voucher_exchange

@router.patch("/voucher_exchanges/mark_used/{voucher_exchange_id}/", response_model=VoucherExchangeRead)
async def mark_voucher_exchange_used_endpoint(request: Request, voucher_exchange_id: int):
    voucher_exchange = await mark_voucher_exchange(request.state.user.get("user_id"), voucher_exchange_id, is_used=True)
    if not voucher_exchange:
        raise HTTPException(status_code=404, detail="Voucher exchange not found")
    return voucher_exchange

@router.patch("/voucher_exchanges/unmark_used/{voucher_exchange_id}/", response_model=VoucherExchangeRead)
async def unmark_voucher_exchange_used_endpoint(request: Request, voucher_exchange_id: int):
    voucher_exchange = await mark_voucher_exchange(request.state.user.get("user_id"), voucher_exchange_id, is_used=False)
    if not voucher_exchange:
        raise HTTPException(status_code=404, detail="Voucher exchange not found")
    return voucher_exchange