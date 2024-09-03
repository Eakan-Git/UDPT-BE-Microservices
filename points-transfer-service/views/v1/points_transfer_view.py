from fastapi import APIRouter, HTTPException
from schemas.points_transfer_schema import Points_TransferCreate, Points_TransferRead
from controllers.points_transfer_controller import create_points_transfer, get_my_sent_transfers, get_my_received_transfers
from controllers.user_controller import user_dependency
from enums import Role

router = APIRouter()

@router.post("/points-transfers/", response_model=Points_TransferRead, description="Create a points transfer, only available for role: admin, manager")
async def create_points_transfer_endpoint(points_transfer: Points_TransferCreate, current_user: user_dependency):
    if not Role.is_granted(current_user.role):
        raise HTTPException(status_code=403, detail="Permission denied")
    points_transfer_data = points_transfer.dict()
    if points_transfer_data["to_user_id"] == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot transfer points to yourself")
    
    points_transfer_data["from_user_id"] = current_user.id

    if current_user.bonus_point < points_transfer_data["points"]:
        raise HTTPException(status_code=400, detail="Insufficient points")

    try:
        new_points_transfer = await create_points_transfer(points_transfer_data)
        return new_points_transfer
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/points-transfers/sent/", response_model=dict, description="Get all points transfers sent by the current user, since transfer is only available for role: admin, manager, this endpoint is only available for those roles too")
async def get_current_user_sent_transfers_endpoint(current_user: user_dependency, page: int = 1, limit: int = 10):
    if not Role.is_granted(current_user.role):
        raise HTTPException(status_code=403, detail="Permission denied")
    points_transfers = await get_my_sent_transfers(current_user.id, page, limit)
    return points_transfers

@router.get("/points-transfers/received/", response_model=dict, description="Get all points transfers received by the current user")
async def get_current_user_received_transfers_endpoint(current_user: user_dependency, page: int = 1, limit: int = 10):
    points_transfers = await get_my_received_transfers(current_user.id, page, limit)
    return points_transfers