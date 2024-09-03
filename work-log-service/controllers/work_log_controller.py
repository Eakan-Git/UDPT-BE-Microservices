from fastapi import HTTPException
from models.mongo import engine
from models.work_log import WorkLog
from controllers.user_controller import get_user_by_id, sudo_get_user_by_id
from datetime import datetime
from helper.time_helper import get_end_of_today, get_start_of_today, is_same_day

async def create_work_log(provided_user_id: int) -> WorkLog:
    
    flag_work_log = await engine.find_one(WorkLog, WorkLog.user_id == provided_user_id, sort=WorkLog.id.desc())
    if flag_work_log and flag_work_log.check_in.date() == datetime.utcnow().date():
        raise HTTPException(status_code=400, detail="User already checked in today")

    work_log_id = await get_next_work_log_id()

    new_work_log = WorkLog(
        id=work_log_id,
        user_id=provided_user_id
    )

    await engine.save(new_work_log)
    return new_work_log

async def check_out(provided_user_id: int) -> WorkLog:
    flag_work_log = await engine.find_one(WorkLog, WorkLog.user_id == provided_user_id, sort=WorkLog.id.desc())
    if not flag_work_log or not flag_work_log.check_in or not is_same_day(flag_work_log.check_in, datetime.utcnow()):
        raise HTTPException(status_code=400, detail="User has not checked in yet")
    if flag_work_log.check_out and is_same_day(flag_work_log.check_out, datetime.utcnow()):
        raise HTTPException(status_code=400, detail="User already checked out today")
    
    flag_work_log.check_out = datetime.utcnow()
    await engine.save(flag_work_log)
    return flag_work_log

async def get_work_logs(page: int, limit: int, start_date: datetime, end_date: datetime) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    work_logs = await engine.find(WorkLog, (WorkLog.created_at >= start_date) & (WorkLog.created_at <= end_date), limit=limit, skip=(page - 1) * limit, sort=WorkLog.id.desc())

    total = await engine.count(WorkLog, (WorkLog.created_at >= start_date) & (WorkLog.created_at <= end_date))

    previous_url = f'/work-logs/?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/work-logs/?page={page + 1}&limit={limit}' if len(work_logs) == limit else None

    total_pages = total // limit + 1 if total % limit else total // limit

    res = {
        "data": [work_log.dict() for work_log in work_logs],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }

    return res

async def get_next_work_log_id() -> int:
    work_log = await engine.find_one(WorkLog, sort=WorkLog.id.desc())
    return work_log.id + 1 if work_log else 1

async def get_my_work_logs(user_id: int, start_date: datetime, end_date: datetime) -> list:
    user = await sudo_get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    work_logs = await engine.find(WorkLog, (WorkLog.user_id == user.id) & (WorkLog.created_at >= start_date) & (WorkLog.created_at <= end_date), sort=WorkLog.id.desc())
    return work_logs

async def get_work_log_by_id(work_log_id: int) -> WorkLog:
    if not isinstance(work_log_id, int) or work_log_id < 1:
        raise HTTPException(status_code=400, detail="Invalid work log ID")

    work_log = await engine.find_one(WorkLog, WorkLog.id == work_log_id)
    
    if not work_log:
        raise HTTPException(status_code=404, detail="Work log not found")
    
    return work_log

async def get_work_logs_by_user_id_and_date_range(user_id: int, start_date: datetime, end_date: datetime) -> list:
    user = await sudo_get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    work_logs = await engine.find(WorkLog, (WorkLog.user_id == user.id) & (WorkLog.created_at >= start_date) & (WorkLog.created_at <= end_date))
    return work_logs

async def update_work_log_note(work_log_id: int, note: str, current_user_id: int) -> WorkLog:
    work_log = await engine.find_one(WorkLog, WorkLog.id == work_log_id, WorkLog.user_id == current_user_id)
    if not work_log:
        raise HTTPException(status_code=404, detail="Work log not found")
    if work_log.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    work_log.note = note
    await engine.save(work_log)
    return work_log