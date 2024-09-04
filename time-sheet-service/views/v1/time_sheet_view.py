from fastapi import APIRouter, HTTPException, Request
from schemas.time_sheet_schema import TimeSheetCreate, TimeSheetRead, TimeSheetUpdate
from controllers.time_sheet_controller import create_time_sheet, get_user_time_sheet, manage_time_sheet, update_my_time_sheet, get_time_sheets
from enums import Role

router = APIRouter()
@router.post("/time_sheets/", response_model=TimeSheetRead)
async def create_time_sheet_endpoint(time_sheet: TimeSheetCreate, request: Request):
    user_id = request.state.user.get("user_id")
    time_sheet_data = time_sheet.dict()
    try:
        new_time_sheet = await create_time_sheet(user_id, time_sheet_data)
        return new_time_sheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/time_sheets/me/", response_model=TimeSheetRead)
async def update_my_time_sheet_endpoint(time_sheet_current_value: TimeSheetUpdate, request: Request):
    current_value = time_sheet_current_value.dict()['current_value']
    user_id = request.state.user.get("user_id")
    try:
        updated_time_sheet = await update_my_time_sheet(user_id, current_value)
        return updated_time_sheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/time_sheets/me/", response_model=TimeSheetRead)
async def get_my_time_sheet_endpoint(request: Request):
    user_id = request.state.user.get("user_id")
    time_sheet = await get_user_time_sheet(user_id)
    if time_sheet is None:
        raise HTTPException(status_code=404, detail="Time sheet not found")
    return time_sheet

@router.get("/time_sheets/", response_model=dict)
async def get_time_sheets_endpoint(request: Request, page: int = 1, limit: int = 10, status: str = None):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    time_sheets = await get_time_sheets(page, limit, status)
    return time_sheets

@router.get("/time_sheets/user/{user_id}/", response_model=TimeSheetRead)
async def get_user_time_sheet_endpoint(user_id: int, request: Request):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    time_sheet = await get_user_time_sheet(user_id)
    if time_sheet is None:
        raise HTTPException(status_code=404, detail="Time sheet not found")
    return time_sheet

@router.patch("/time_sheets/{time_sheet_id}/", response_model=TimeSheetRead)
async def manage_time_sheet_endpoint(time_sheet_id: int, status: str, request: Request):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    try:
        managed_time_sheet = await manage_time_sheet(time_sheet_id, status)
        return managed_time_sheet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))