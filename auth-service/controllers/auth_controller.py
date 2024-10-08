from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException
import os
from schemas.auth_schema import TokenData
import json
from rabbitmq.rpc_client import AuthRpcClient
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

USER_SERVICE_BASE_URL = os.getenv("USER_SERVICE_BASE_URL")

from models.redis import set_redis, delete_redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def authenticate_user(username: str, password: str):
    auth_rpc = AuthRpcClient()
    await auth_rpc.setup()
    data = json.dumps({"username": username, "password": password})
    try:
        response = await auth_rpc.call(data)
    except Exception as e:
        pass
    finally:
        await auth_rpc.close()
    return response

def create_access_token(data: TokenData, expires_delta: timedelta = None):
    to_encode = data.dict()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    set_redis(encoded_jwt, data.username)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    
async def revoke_token(token: str):
    try:
        delete_redis(token)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    return True