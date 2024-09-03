from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import httpx

from schemas.auth_schema import Token

from config import TOKEN_URL
from config import service_urls


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    auth_service_url = service_urls.get("AUTH")

    form_data_dict = {
        "username": form_data.username,
        "password": form_data.password,
        "grant_type": form_data.grant_type,
        "client_id": form_data.client_id,
        "client_secret": form_data.client_secret,
    }
    
    async with httpx.AsyncClient() as client:
        request_url = f"{auth_service_url}/login"
        response = await client.post(request_url, data=form_data_dict)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        
        return response.json()
    
@router.post("/auth/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    auth_service_url = service_urls.get("AUTH")
    
    async with httpx.AsyncClient() as client:
        request_url = f"{auth_service_url}/logout"
        response = await client.post(request_url, headers={"Authorization": f"Bearer {token}"})
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json())
        
        return response.json()