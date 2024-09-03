from fastapi import HTTPException
from models.mongo import engine
from models.activity import Activity

async def create_activity(activity_data: dict) -> Activity:
    activity_id = await get_next_activity_id()
    activity_data["id"] = activity_id
    activity = Activity(**activity_data)
    await engine.save(activity)
    return activity

async def get_next_activity_id() -> int:
    last_activity = await engine.find_one(Activity, sort=Activity.id.desc())
    return last_activity.id + 1 if last_activity else 1

async def get_activities(page: int, limit: int) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    activities = await engine.find(Activity, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/activities/?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/activities/?page={page + 1}&limit={limit}' if len(activities) == limit else None
    
    total = await engine.count(Activity)
    total_pages = total // limit + 1 if total % limit else total // limit
    
    res = {
        "data": [activity.dict() for activity in activities],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res

async def get_activity_by_id(activity_id: int) -> Activity:
    if not isinstance(activity_id, int) or activity_id < 1:
        raise HTTPException(status_code=400, detail="Invalid activity id")
    activity = await engine.find_one(Activity, Activity.id == activity_id)
    return activity

async def update_activity(activity_id: int, activity_data: dict) -> Activity:
    if not isinstance(activity_id, int) or activity_id < 1:
        raise HTTPException(status_code=400, detail="Invalid activity id")
    activity = await get_activity_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    for key, value in activity_data.items():
        if hasattr(activity, key) and value is not None:
            setattr(activity, key, value)
    await engine.save(activity)
    return activity
