from fastapi import APIRouter, HTTPException
from schemas.activity_schema import ActivityCreate, ActivityRead, ActivityUpdate
from controllers.activity_controller import create_activity, get_activity_by_id, update_activity, get_activities
from controllers.user_controller import user_dependency
from enums import ActivityType, Role

router = APIRouter()

@router.post("/activities/", response_model=ActivityRead)
async def create_activity_endpoint(activity: ActivityCreate, current_user: user_dependency):
    if not Role.is_granted(current_user.role):
        raise HTTPException(status_code=403, detail="Permission denied")
    activity_data = activity.dict()
    activity_type = activity_data.get("type")
    activity_data["type"] = activity_type.lower()
    if ActivityType.is_valid(activity_type) is False:
        raise HTTPException(status_code=400, detail="Invalid activity type")
    try:
        new_activity = await create_activity(activity_data)
        return new_activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activities/{activity_id}", response_model=ActivityRead)
async def get_activity_by_activity_id_endpoint(activity_id: int, current_user: user_dependency):
    activity = await get_activity_by_id(activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity

@router.get("/activities/", response_model=dict)
async def get_activities_endpoint(current_user: user_dependency, page: int = 1, limit: int = 10):
    activities = await get_activities(page, limit)
    return activities

@router.put("/activities/{activity_id}", response_model=ActivityRead)
async def update_activity_endpoint(activity_id: int, activity: ActivityUpdate, current_user: user_dependency):
    if not Role.is_granted(current_user.role):
        raise HTTPException(status_code=403, detail="Permission denied")
    activity_data = activity.dict()
    try:
        updated_activity = await update_activity(activity_id, activity_data)
        return updated_activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))