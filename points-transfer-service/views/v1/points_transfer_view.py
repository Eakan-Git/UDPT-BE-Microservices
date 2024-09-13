from fastapi import APIRouter, HTTPException, Request
from schemas.points_transfer_schema import Points_TransferCreate, Points_TransferRead
from controllers.points_transfer_controller import create_points_transfer, get_my_sent_transfers, get_my_received_transfers
from enums import Role
from rabbitmq.get_user_rpc_client import GetUserRpcClient
import json

router = APIRouter()

@router.post("/points-transfers/", response_model=Points_TransferRead, description="Create a points transfer, only available for role: admin, manager")
async def create_points_transfer_endpoint(points_transfer: Points_TransferCreate, request: Request):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    current_user_id = request.state.user.get("user_id")
    points_transfer_data = points_transfer.dict()
    if points_transfer_data["to_user_id"] == current_user_id:
        raise HTTPException(status_code=400, detail="Cannot transfer points to yourself")
    
    points_transfer_data["from_user_id"] = current_user_id

    get_user_rpc_client = GetUserRpcClient()

    try:
        await get_user_rpc_client.setup()
        current_user_query_data = json.dumps({"user_id": current_user_id})
        current_user_query_response = await get_user_rpc_client.call(current_user_query_data)
    except Exception as e:
        print(str(e))
    finally:
        await get_user_rpc_client.close()
    current_user = json.loads(current_user_query_response)
    if current_user.get("error"):
        raise HTTPException(status_code=404, detail="User not found")
    
    current_user_bonus_point = current_user.get("bonus_point")

    if current_user_bonus_point < points_transfer_data["points"]:
        raise HTTPException(status_code=400, detail="Insufficient points")

    try:
        new_points_transfer = await create_points_transfer(points_transfer_data)
        try:
            if new_points_transfer.get("error"):
                raise HTTPException(status_code=400, detail=new_points_transfer.get("error"))
        except:
            pass
        return new_points_transfer
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/points-transfers/sent/", response_model=dict, description="Get all points transfers sent by the current user, since transfer is only available for role: admin, manager, this endpoint is only available for those roles too")
async def get_current_user_sent_transfers_endpoint(request: Request, page: int = 1, limit: int = 10):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    points_transfers = await get_my_sent_transfers(request.state.user.get("user_id"), page, limit)
    return points_transfers

@router.get("/points-transfers/received/", response_model=dict, description="Get all points transfers received by the current user")
async def get_current_user_received_transfers_endpoint(request: Request, page: int = 1, limit: int = 10):
    points_transfers = await get_my_received_transfers(request.state.user.get("user_id"), page, limit)
    return points_transfers