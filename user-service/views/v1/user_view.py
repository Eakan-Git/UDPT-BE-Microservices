from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from schemas.user_schema import UserCreate, UserRead, UserUpdate, UserChangePassword, VerifyPassword
from controllers.user_controller import create_user, get_user_by_id, get_user_paginate, update_user, delete_user, change_password
from controllers.user_controller import user_dependency, authenticate_user
from enums import Role

router = APIRouter()

@router.get("/users/me/", response_model=UserRead)
def get_current_user(current_user: user_dependency):
    return current_user

@router.post("/users/", response_model=UserRead)
async def create_user_endpoint(user: UserCreate, current_user: user_dependency):
    if not Role.is_granted(current_user.role):
        raise HTTPException(status_code=403, detail="Unauthorized to create user")
    user_data = user.dict()
    try:
        new_user = await create_user(user_data)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users/{user_id}", response_model=UserRead)
async def get_user_by_id_endpoint(user_id: int, current_user: user_dependency):
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/users/", response_model=dict)
async def get_users_endpoint(current_user: user_dependency, page: int = 1, limit: int = 10):
    users = await get_user_paginate(page, limit)
    return users

@router.put("/users/change-password", response_model=UserRead)
async def change_password_endpoint(password_data: UserChangePassword, current_user: user_dependency):
    password_data = password_data.dict()
    old_password = password_data.pop("old_password")
    new_password = password_data.pop("new_password")
    updated_user = await change_password(current_user.id, old_password, new_password)
    return updated_user

@router.patch("/users/{user_id}", response_model=UserRead)
async def update_user_endpoint(user_id: int, user: UserUpdate, current_user: user_dependency):
    user_data = user.model_dump()
    if user_data.get("bonus_point") is not None or user_data.get("role") is not None:
        if not Role.is_granted(current_user.role):
            raise HTTPException(status_code=403, detail="Unauthorized to update bonus point")
    updated_user = await update_user(user_id, user_data)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/users/{user_id}", response_model=dict)
async def delete_user_endpoint(user_id: int, current_user: user_dependency):
    if not Role.is_granted(current_user.role):
        raise HTTPException(status_code=403, detail="Unauthorized to delete user")
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"detail": "User deleted successfully"}
