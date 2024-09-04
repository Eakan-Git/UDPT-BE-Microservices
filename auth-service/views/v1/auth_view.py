from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
import json
from controllers.auth_controller import create_access_token, revoke_token
from controllers.auth_controller import authenticate_user
from schemas.auth_schema import Token, TokenData
from config import ACCESS_TOKEN_EXPIRE_MINUTES, TOKEN_URL

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    response = await authenticate_user(form_data.username, form_data.password)
    response = json.loads(response)
    
    if response.get("error"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    _username = response.get("username")
    _user_id = response.get("user_id")
    _role = response.get("role")

    token_data = TokenData(username=_username, user_id=_user_id, role=_role)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)
    user_data = token_data.dict()
    return {"access_token": access_token, "token_type": "bearer", "user": user_data}

@router.post("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    if not await revoke_token(token):
        raise HTTPException(status_code=500, detail="Internal server error")
    return {"message": "Successfully logged out"}