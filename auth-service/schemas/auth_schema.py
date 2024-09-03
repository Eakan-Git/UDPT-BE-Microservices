from pydantic import BaseModel

class TokenData(BaseModel):
    username: str
    user_id: int
    role: str
class Token(BaseModel):
    access_token: str
    token_type: str
    user: TokenData