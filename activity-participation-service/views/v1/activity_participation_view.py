from fastapi import APIRouter, HTTPException
from schemas.activity_participation_schema import Activity_ParticipationCreate, Activity_ParticipationRead
from controllers.activity_participation_controller import create_activity_participation, get_activity_participation_by_id, get_activity_participations_by_user_id, get_activity_participations_by_activity_id, get_my_activity_participations
from controllers.user_controller import user_dependency
from enums import Role

router = APIRouter()

@router.post("/activity_participations/", response_model=Activity_ParticipationRead)
async def participate_activity_endpoint(activity_participation: Activity_ParticipationCreate, current_user: user_dependency):
    activity_participation_data = activity_participation.dict()
    activity_participation_data["user_id"] = current_user.id
    try:
        new_activity_participation = await create_activity_participation(activity_participation_data)
        return new_activity_participation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/activity_participations/", response_model=dict)
async def get_activity_participations_by_activity_id_endpoint(activity_id: int, current_user: user_dependency, page: int = 1, limit: int = 10):
    activity_participations = await get_activity_participations_by_activity_id(activity_id, page, limit)
    return activity_participations

@router.get("/activity_participations/me", response_model=dict)
async def get_activity_participations_by_current_user_endpoint(current_user: user_dependency, page: int = 1, limit: int = 10):
    activity_participations = await get_my_activity_participations(current_user.id, page, limit)
    return activity_participations

@router.get("/activity_participations/{activity_participation_id}", response_model=Activity_ParticipationRead)
async def get_activity_participation_by_activity_participation_id_endpoint(activity_participation_id: int, current_user: user_dependency):
    activity_participation = await get_activity_participation_by_id(activity_participation_id)
    if activity_participation is None:
        raise HTTPException(status_code=404, detail="Activity participation not found")
    return activity_participation

@router.get("/activity_participations/user/{user_id}", response_model=dict)
async def get_activity_participations_by_user_id_endpoint(user_id: int, current_user: user_dependency, page: int = 1, limit: int = 10):
    activity_participations = await get_activity_participations_by_user_id(user_id, page, limit)
    return activity_participations