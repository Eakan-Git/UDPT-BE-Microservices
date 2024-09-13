from fastapi import HTTPException, status
from models.mongo import engine
from models.activity_participation import Activity_Participation
from helper import time_helper
from rabbitmq.get_activity_rpc_client import GetActivityRpcClient
import json

async def create_activity_participation(activity_participation_data: dict) -> Activity_Participation:
    participation_flag = await engine.find_one(Activity_Participation, Activity_Participation.user_id == activity_participation_data.get("user_id"), Activity_Participation.activity_id == activity_participation_data.get("activity_id"))
    if participation_flag:
        return {"error": "User has already participated in this activity"}
    
    activity_participation_id = await get_next_activity_participation_id()
    activity_participation_data["id"] = activity_participation_id
    
    get_activity_rpc_client = GetActivityRpcClient()
    try:
        await get_activity_rpc_client.setup()
        call_data = {
            "activity_id": activity_participation_data.get("activity_id")
        }
        requesting_activity = await get_activity_rpc_client.call(json.dumps(call_data))
        requesting_activity = json.loads(requesting_activity)
        if requesting_activity.get("error"):
            return {"error": "Activity not found"}
        if not time_helper.is_greater_than(time_helper.convert_to_datetime(requesting_activity.get('to_date')), time_helper.get_current_datetime()):
            return {"error": "Activity has ended"}
    except Exception as e:
        print(f"Error fetching activity data: {e}")
    finally:
        await get_activity_rpc_client.close()
    
    activity_participation = Activity_Participation(**activity_participation_data)
    await engine.save(activity_participation)
    return activity_participation

async def get_next_activity_participation_id() -> int:
    last_activity_participation = await engine.find_one(Activity_Participation, sort=Activity_Participation.id.desc())
    return last_activity_participation.id + 1 if last_activity_participation else 1

async def get_activity_participations_by_activity_id(activity_id: int, page: int, limit: int) -> dict:
    if not isinstance(activity_id, int) or activity_id < 1:
        raise HTTPException(status_code=400, detail="Invalid activity id")
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    activity_participations = await engine.find(Activity_Participation, {"activity_id": activity_id}, limit=limit, skip=(page - 1) * limit, sort=Activity_Participation.activity_points.desc())

    previous_url = f'/activity_participations/?activity_id={activity_id}&page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/activity_participations/?activity_id={activity_id}&page={page + 1}&limit={limit}' if len(activity_participations) == limit else None

    total = await engine.count(Activity_Participation, {"activity_id": activity_id})
    total_pages = total // limit + 1 if total % limit else total // limit

    res = {
        "data": [activity_participation.dict() for activity_participation in activity_participations],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }

    return res

async def get_activity_participation_by_id(activity_participation_id: int) -> Activity_Participation:
    if not isinstance(activity_participation_id, int) or activity_participation_id < 1:
        raise HTTPException(status_code=400, detail="Invalid activity participation id")
    activity_participation = await engine.find_one(Activity_Participation, Activity_Participation.id == activity_participation_id)
    return activity_participation

async def get_my_activity_participations(user_id: int, page: int, limit: int) -> dict:
    if not isinstance(user_id, int) or user_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user id")
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    activity_participations = await engine.find(Activity_Participation, {"user_id": user_id}, limit=limit, skip=(page - 1) * limit)

    previous_url = f'/activity_participations/me?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/activity_participations/me?page={page + 1}&limit={limit}' if len(activity_participations) == limit else None

    total = await engine.count(Activity_Participation, {"user_id": user_id})
    total_pages = total // limit + 1 if total % limit else total // limit

    res = {
        "data": [activity_participation.dict() for activity_participation in activity_participations],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }

    return res

async def get_activity_participations_by_user_id(user_id: int, page: int, limit: int) -> dict:
    if not isinstance(user_id, int) or user_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user id")
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    activity_participations = await engine.find(Activity_Participation, {"user_id": user_id}, limit=limit, skip=(page - 1) * limit)

    total = await engine.count(Activity_Participation, {"user_id": user_id})
    total_pages = total // limit + 1 if total % limit else total // limit

    previous_url = f'/activity_participations/user/{user_id}?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/activity_participations/user/{user_id}?page={page + 1}&limit={limit}' if total > page * limit else None

    res = {
        "data": [activity_participation.dict() for activity_participation in activity_participations],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }

    return res

async def update_activity_participation_points(activity_participation_id: int, activity_participation_data: dict) -> Activity_Participation:
    if not isinstance(activity_participation_id, int) or activity_participation_id < 1:
        raise HTTPException(status_code=400, detail="Invalid activity participation id")
    activity_participation = await engine.find_one(Activity_Participation, Activity_Participation.id == activity_participation_id)
    if not activity_participation:
        raise HTTPException(status_code=404, detail="Activity participation not found")
    
    activity_participation.activity_points = activity_participation_data.get("activity_points", activity_participation.activity_points)
    await engine.save(activity_participation)
    return activity_participation