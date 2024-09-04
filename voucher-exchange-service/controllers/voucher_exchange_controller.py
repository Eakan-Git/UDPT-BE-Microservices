from fastapi import HTTPException
from models.mongo import engine
from models.voucher_exchange import Voucher_Exchange
from datetime import datetime
from rabbitmq.get_user_rpc_client import GetUserRpcClient
from rabbitmq.get_voucher_rpc_client import GetVoucherRpcClient
from rabbitmq.patch_user_rpc_client import PatchUserRpcClient
import json

async def create_voucher_exchange(voucher_exchange_data: dict) -> Voucher_Exchange:    
    get_voucher_rpc_client = GetVoucherRpcClient()
    await get_voucher_rpc_client.setup()
    data = json.dumps({"voucher_id": voucher_exchange_data.get("voucher_id")})
    try:
        response = await get_voucher_rpc_client.call(data)
    except Exception as e:
        pass
    finally:
        await get_voucher_rpc_client.close()
    requesting_voucher = json.loads(response)

    get_user_rpc_client = GetUserRpcClient()
    await get_user_rpc_client.setup()

    data = json.dumps({"user_id": voucher_exchange_data.get("user_id")})
    try:
        response = await get_user_rpc_client.call(data)
    except Exception as e:
        pass
    finally:
        await get_user_rpc_client.close()
    requesting_user = json.loads(response)

    if requesting_voucher.get("error"):
        return {"error": "Voucher not found"}
    if not requesting_user:
        return {"error": "User not found"}
    
    if requesting_voucher.get("require_point") > requesting_user.get("bonus_point"):
        raise HTTPException(status_code=400, detail="Not enough point to exchange this voucher")

    next_voucher_exchange_id = await get_next_voucher_exchange_id()
    voucher_exchange_data["id"] = next_voucher_exchange_id
    voucher_exchange_data["voucher_title"] = requesting_voucher.get("title")
    voucher_exchange_data["voucher_description"] = requesting_voucher.get("description")
    voucher_exchange_data["point_used"] = requesting_voucher.get("require_point")

    requesting_user["bonus_point"] -= requesting_voucher["require_point"]

    voucher_exchange = Voucher_Exchange(**voucher_exchange_data)
    await engine.save(voucher_exchange)
    patch_user_rpc_client = PatchUserRpcClient()
    await patch_user_rpc_client.setup()

    requesting_user_id = requesting_user.get("id")
    requesting_user_bonus_point = requesting_user.get("bonus_point")
    patch_data = {
        "user_id": requesting_user_id,
        "patch_data": {
            "bonus_point": requesting_user_bonus_point
        }
    }
    try:
        await patch_user_rpc_client.call(json.dumps(patch_data))
    except Exception as e:
        print(e)
    finally:
        await patch_user_rpc_client.close()
    return voucher_exchange

async def get_voucher_exchange(voucher_exchange_id: int) -> Voucher_Exchange:
    voucher_exchange = await engine.find_one(Voucher_Exchange, Voucher_Exchange.id == voucher_exchange_id)
    return voucher_exchange

async def get_voucher_exchanges(page: int = 1, limit: int = 10) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    voucher_exchanges = await engine.find(Voucher_Exchange, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/voucher_exchanges/?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/voucher_exchanges/?page={page + 1}&limit={limit}' if len(voucher_exchanges) == limit else None
    
    total = await engine.count(Voucher_Exchange)
    total_pages = total // limit + 1 if total % limit else total // limit
    
    res = {
        "data": [voucher_exchange.dict() for voucher_exchange in voucher_exchanges],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res
async def get_my_voucher_exchanges(page: int = 1, limit: int = 10, user_id: int = None) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    voucher_exchanges = await engine.find(Voucher_Exchange, Voucher_Exchange.user_id == user_id, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/voucher_exchanges/me/?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/voucher_exchanges/me/?page={page + 1}&limit={limit}' if len(voucher_exchanges) == limit else None
    
    total = await engine.count(Voucher_Exchange, Voucher_Exchange.user_id == user_id)
    total_pages = total // limit + 1 if total % limit else total // limit
    
    res = {
        "data": [voucher_exchange.dict() for voucher_exchange in voucher_exchanges],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res

async def mark_voucher_exchange(current_user_id: int, voucher_exchange_id: int, is_used: bool) -> Voucher_Exchange:
    voucher_exchange = await engine.find_one(Voucher_Exchange, Voucher_Exchange.id == voucher_exchange_id, Voucher_Exchange.user_id == current_user_id)
    if not voucher_exchange:
        return None
    voucher_exchange.is_used = is_used
    voucher_exchange.updated_at = datetime.utcnow()
    await engine.save(voucher_exchange)
    return voucher_exchange

async def get_next_voucher_exchange_id() -> int:
    last_voucher_exchange = await engine.find_one(Voucher_Exchange, sort=Voucher_Exchange.id.desc())
    return last_voucher_exchange.id + 1 if last_voucher_exchange else 1