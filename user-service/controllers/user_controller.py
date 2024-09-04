from fastapi import HTTPException, Depends, status
from typing import Annotated
from jose import JWTError, jwt
from models.mongo import engine
from models.user import User
from datetime import datetime
from controllers.auth_controller import get_password_hash, verify_password

from fastapi.security import OAuth2PasswordBearer

from config import SECRET_KEY, ALGORITHM, TOKEN_URL

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Since the token is already passed through the middleware, we can decode it directly
        token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = token_data.get("username")
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(username)

    if user is None:
        raise credentials_exception
    return user

user_dependency = Annotated[dict, Depends(get_current_user)]

async def authenticate_user(username: str, password: str):
    user = await sudo_get_user_by_username(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    user.__dict__.pop("hashed_password")
    return user

async def create_user(user_data: dict) -> User:
    flag_user = await get_user_by_username(user_data["username"])
    if flag_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    user_id = await get_next_user_id()
    user_data["id"] = user_id
    user = User(**user_data)
    await engine.save(user)
    return user

async def get_next_user_id() -> int:
    last_user = await engine.find_one(User, sort=User.id.desc())
    return last_user.id + 1 if last_user else 1

async def get_user_by_id(user_id: int) -> User:
    user = await engine.find_one(User, User.id == user_id, {"is_locked": False})
    return user

async def sudo_get_user_by_id(user_id: int) -> User:
    if not isinstance(user_id, int) or user_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user id")
    user = await engine.find_one(User, User.id == user_id)
    return user

async def get_user_by_username(username: str) -> User:
    if not isinstance(username, str) or not username:
        raise HTTPException(status_code=400, detail="Invalid username")
    user = await engine.find_one(User, User.username == username)
    if not user:
        return None
    if user.is_locked:
        raise HTTPException(status_code=400, detail="User is locked")
    return user

async def get_user_paginate(page: int, limit: int) -> dict:
    if not isinstance(page, int) or page < 1:
        raise HTTPException(status_code=400, detail="Invalid page value")
    if not isinstance(limit, int) or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid limit value")
    
    users = await engine.find(User, {"is_locked": False}, limit=limit, skip=(page - 1) * limit)
    
    previous_url = f'/users?page={page - 1}&limit={limit}' if page > 1 else None
    next_url = f'/users?page={page + 1}&limit={limit}' if len(users) == limit else None
    
    total = await engine.count(User)
    total_pages = total // limit + 1 if total % limit else total // limit

    for user in users:
        user.__dict__.pop("hashed_password")
        
    res = {
        "data": [user.dict() for user in users],
        "current_page": page,
        "previous": previous_url,
        "next": next_url,
        "total": total,
        "total_pages": total_pages,
        "limit": limit
    }
    
    return res

async def update_user(user_id: int, user_data: dict) -> User:
    if not isinstance(user_id, int) or user_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user id")
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid user data")
    
    user = await get_user_by_id(user_id)
    if user:
        for key, value in user_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        user.updated_at = datetime.utcnow()
        await engine.save(user)
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

async def sudo_get_user_by_username(username: str) -> User:
    if not isinstance(username, str) or not username:
        raise HTTPException(status_code=400, detail="Invalid username")
    user = await engine.find_one(User, User.username == username)
    return user

async def change_password(user_id: int, old_password: str, new_password: str) -> bool:
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if verify_password(old_password, user.hashed_password):
        user.hashed_password = get_password_hash(new_password)
        user.is_channged_default_password = True
        user.updated_at = datetime.utcnow()
        await engine.save(user)
        return user
    raise HTTPException(status_code=400, detail="Incorrect given password")

# soft delete, set is_locked to True
async def delete_user(user_id: int) -> bool:
    if not isinstance(user_id, int) or user_id < 1:
        raise HTTPException(status_code=400, detail="Invalid user id")

    user = await get_user_by_id(user_id)
    if user:
        user.is_locked = True
        user.updated_at = datetime.utcnow()
        await engine.save(user)
        return True
    return False
