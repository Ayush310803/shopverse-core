from fastapi import Depends, HTTPException
from app.auth import verify_token
from app.crud.user_crud import get_user_by_username
from fastapi.security import OAuth2PasswordBearer
from app.auth import is_token_blacklisted  

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/User_login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="You have been logged out")

    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Token payload is invalid")
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
