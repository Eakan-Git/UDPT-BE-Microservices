from fastapi import APIRouter, HTTPException, Request
from schemas.work_log_schema import WorkLogRead, WorkLogUpdateNote
from controllers.work_log_controller import create_work_log, get_work_log_by_id, update_work_log_note,  get_my_work_logs, get_work_logs_by_user_id_and_date_range, check_out, get_work_logs
from datetime import datetime
from helper.time_helper import get_start_of_today, get_end_of_today
from enums import Role

router = APIRouter()

@router.post("/work-logs/check-in", response_model=WorkLogRead)
async def user_check_in_endpoint(request: Request):
    provided_user_id = request.state.user.get("user_id")
    new_work_log = await create_work_log(provided_user_id)
    return new_work_log

@router.patch("/work-logs/check-out", response_model=WorkLogRead)
async def user_check_out_endpoint(request: Request):
    provided_user_id = request.state.user.get("user_id")
    new_work_log = await check_out(provided_user_id)
    return new_work_log

@router.get("/work-logs/", response_model=dict)
async def get_work_logs_endpoint(request: Request, page: int = 1, limit: int = 10, start_date: datetime = get_start_of_today(), end_date: datetime = get_end_of_today()):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    return await get_work_logs(page, limit, start_date, end_date)

@router.get("/work-logs/me/", response_model=list[WorkLogRead])
async def get_my_work_logs_in_date_range_endpoint(request: Request, start_date: datetime = get_start_of_today(), end_date: datetime = get_end_of_today()):
    provided_user_id = request.state.user.get("user_id")
    return await get_my_work_logs(provided_user_id, start_date, end_date)

@router.get("/work-logs/{work_log_id}", response_model=WorkLogRead)
async def get_work_log_by_id_endpoint(work_log_id: int):
    return await get_work_log_by_id(work_log_id)

@router.get("/work-logs/user/{user_id}", response_model=list[WorkLogRead])
async def get_work_logs_by_user_id_in_date_range_endpoint(request: Request, user_id: int, start_date: datetime = get_start_of_today(), end_date: datetime = get_end_of_today()):
    if not Role.is_granted(request.state.user.get("role")):
        raise HTTPException(status_code=403, detail="Permission denied")
    return await get_work_logs_by_user_id_and_date_range(user_id, start_date, end_date)

@router.patch("/work-logs/note/{work_log_id}", response_model=WorkLogRead)
async def update_work_log_note_endpoint(work_log_id: int, data: WorkLogUpdateNote, request: Request):
    provided_user_id = request.state.user.get("user_id")
    return await update_work_log_note(work_log_id, data.note, provided_user_id)