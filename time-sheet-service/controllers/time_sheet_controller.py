from fastapi import HTTPException
from models.mongo import engine
from models.time_sheet import Time_Sheet
from enums import TimeSheet, TimeSheetStatus
from helper import time_helper

async def create_time_sheet(user_id: int, time_sheet_data: dict = TimeSheet.DEFAULT) -> Time_Sheet:
    flag_time_sheet = await engine.find_one(Time_Sheet, Time_Sheet.user_id == user_id)
    if flag_time_sheet:
        raise HTTPException(status_code=400, detail="Time sheet already exists")
    default_time_sheet = TimeSheet.DEFAULT.copy()
    default_time_sheet.update(time_sheet_data)
    time_sheet_id = await get_next_time_sheet_id()
    default_time_sheet["id"] = time_sheet_id
    default_time_sheet["user_id"] = user_id
    time_sheet = Time_Sheet(**default_time_sheet)
    await engine.save(time_sheet)
    return time_sheet

async def get_next_time_sheet_id() -> int:
    last_time_sheet = await engine.find_one(Time_Sheet, sort=Time_Sheet.id.desc())
    return last_time_sheet.id + 1 if last_time_sheet else 1

async def get_user_time_sheet(user_id: int) -> dict:
    time_sheet = await engine.find_one(Time_Sheet, Time_Sheet.user_id == user_id)
    return time_sheet

async def update_my_time_sheet(user_id: int, current_value: dict) -> Time_Sheet:
    if not TimeSheet.is_valid_value(current_value):
        raise HTTPException(status_code=400, detail="Invalid time sheet value")
    
    db_time_sheet = await get_user_time_sheet(user_id)
    if not db_time_sheet:
        raise HTTPException(status_code=404, detail="Time sheet not found")
    
    if db_time_sheet.status == TimeSheetStatus.APPROVED.value:
        previous_value = db_time_sheet.current_value
        db_time_sheet.current_value = current_value
        db_time_sheet.previous_value = previous_value

    else:
        db_time_sheet.current_value = current_value

    db_time_sheet.updated_at = time_helper.get_current_datetime()
    db_time_sheet.status = TimeSheetStatus.PENDING.value
    db_time_sheet = Time_Sheet(**db_time_sheet.dict())

    await engine.save(db_time_sheet)
    return db_time_sheet

async def get_time_sheets(page: int, limit: int, status: str = None) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    query = {}
    if status:
        if not TimeSheetStatus.is_valid(status.lower()):
            raise HTTPException(status_code=400, detail="Invalid time sheet status value")
        query["status"] = status.lower()
    
    time_sheets = await engine.find(Time_Sheet, query, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/time_sheets/?page={page - 1}&limit={limit}&status={status}' if page > 1 else None
    next_url = f'/time_sheets/?page={page + 1}&limit={limit}&status={status}' if len(time_sheets) == limit else None
    
    total = await engine.count(Time_Sheet, query)
    total_pages = total // limit + 1 if total % limit else total // limit
    
    res = {
        "data": [time_sheet.dict() for time_sheet in time_sheets],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res

async def manage_time_sheet(time_sheet_id: int, status: str) -> Time_Sheet:
    time_sheet = await engine.find_one(Time_Sheet, Time_Sheet.id == time_sheet_id)
    if not time_sheet:
        raise HTTPException(status_code=404, detail="Time sheet not found")
    if not TimeSheetStatus.is_valid(status.lower()):
        raise HTTPException(status_code=400, detail="Invalid time sheet status")
    
    if time_sheet.status == TimeSheetStatus.APPROVED.value:
        raise HTTPException(status_code=400, detail="Cannot change status of an approved time sheet")

    time_sheet.status = status.lower()

    if time_sheet.status == TimeSheetStatus.APPROVED.value:
        time_sheet.previous_value = time_sheet.current_value

    await engine.save(time_sheet)
    return time_sheet