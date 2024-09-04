from fastapi import HTTPException
import asyncio
from models.mongo import engine
from models.points_transfer import Points_Transfer
from rabbitmq.get_user_rpc_client import GetUserRpcClient
from rabbitmq.patch_user_rpc_client import PatchUserRpcClient
import json

async def create_points_transfer(points_transfer_data: dict) -> Points_Transfer:
    from_user_id = points_transfer_data["from_user_id"]
    to_user_id = points_transfer_data["to_user_id"]

    get_user_rpc_client = GetUserRpcClient()
    await get_user_rpc_client.setup()

    data = json.dumps({"user_id": from_user_id})
    response = await get_user_rpc_client.call(data)
    response = json.loads(response)

    if response.get("error"):
        return {"error": "Request user not found"}
    requesting_user = response

    data = json.dumps({"user_id": to_user_id})
    response = await get_user_rpc_client.call(data)
    response = json.loads(response)

    if response.get("error"):
        return {"error": "Receive user not found"}
    receiving_user = json.loads(response)
    
    # requesting_user = await get_user_by_id(points_transfer_data["from_user_id"])
    # receiving_user = await get_user_by_id(points_transfer_data["to_user_id"])
    # if not requesting_user or not receiving_user:
    #     raise HTTPException(status_code=404, detail="User not found")
    new_requesting_user_bonus_points = requesting_user.bonus_point - points_transfer_data["points"]
    new_receiving_user_bonus_points = receiving_user.bonus_point + points_transfer_data["points"]
    points_transfer_id = await get_next_points_transfer_id()
    points_transfer_data["id"] = points_transfer_id
    points_transfer = Points_Transfer(**points_transfer_data)
    print(points_transfer)
    print("before save")
    patch_user_rpc_client = PatchUserRpcClient()
    await patch_user_rpc_client.setup()

    request_data = json.dumps({"bonus_point": new_requesting_user_bonus_points})
    receive_data = json.dumps({"bonus_point": new_receiving_user_bonus_points})

    await asyncio.gather(
        engine.save(points_transfer),
        patch_user_rpc_client.call(requesting_user.id, request_data),
        patch_user_rpc_client.call(receiving_user.id, receive_data)
    )
    return points_transfer

async def get_next_points_transfer_id() -> int:
    last_points_transfer = await engine.find_one(Points_Transfer, sort=Points_Transfer.id.desc())
    return last_points_transfer.id + 1 if last_points_transfer else 1

async def get_my_sent_transfers(user_id: int, page: int, limit: int) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    points_transfers = await engine.find(Points_Transfer, Points_Transfer.from_user_id == user_id, limit=limit, skip=(page - 1) * limit)

    previous_url = f'/points-transfers/sent/?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/points-transfers/sent/?page={page + 1}&limit={limit}' if len(points_transfers) == limit else None

    total = await engine.count(Points_Transfer, Points_Transfer.from_user_id == user_id)
    total_pages = total // limit + 1 if total % limit else total // limit

    res = {
        "data": [points_transfer.dict() for points_transfer in points_transfers],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }

    return res

async def get_my_received_transfers(user_id: int, page: int, limit: int) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    points_transfers = await engine.find(Points_Transfer, Points_Transfer.to_user_id == user_id, limit=limit, skip=(page - 1) * limit)

    previous_url = f'/points-transfers/received/?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/points-transfers/received/?page={page + 1}&limit={limit}' if len(points_transfers) == limit else None

    total = await engine.count(Points_Transfer, Points_Transfer.to_user_id == user_id)
    total_pages = total // limit + 1 if total % limit else total // limit

    res = {
        "data": [points_transfer.dict() for points_transfer in points_transfers],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }

    return res