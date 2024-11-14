from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import get_current_user, oauth2_scheme
from app.auth import create_access_token, invalidate_token
from app.models.users import Admin
import logging
from app.crud.user_crud import create_seller_profile, create_buyer_profile
from app.schemas.userschema import UserCreate,User, UserResponse
from datetime import datetime

router = APIRouter()
ADMIN_SECRET_CODE = "accesstoadmin"
logging.basicConfig(filename="login_activity.log", level=logging.INFO, format="%(levelname)s - %(message)s",)

@router.post("/User_registration/", response_model=UserResponse)
async def register_user(user: UserCreate):
    existing_user = User.objects(username=user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    role = user.role

    if user.secret_code == ADMIN_SECRET_CODE:
        role = "admin"
    else:
        raise HTTPException(status_code=400, detail="do not have access to become admin")

    new_user = None  

    if role == "buyer":
        new_user = create_buyer_profile(user)

    elif role == "seller":
        new_user = create_seller_profile(user)

    elif role == "admin":
        new_user = Admin(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=role,
            phone_no= user.phone_no
        )
        new_user.set_password(user.password)
        new_user.save()

    if new_user is None:
        raise HTTPException(status_code=500, detail="Error creating user")

    logging.info(f"New user {user.username} registered at {datetime.now()}")

    return UserResponse(
        username=new_user.username,
        email=new_user.email,
        role=new_user.role,
        phone_no=new_user.phone_no
    )

@router.post("/User_login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = User.objects.get(username=form_data.username)
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    logging.info(f"User {user.username} logged in at {datetime.now()}")
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/User_logout/")
async def logout(token: str = Depends(oauth2_scheme),current_user: UserResponse = Depends(get_current_user)):
    invalidate_token(token)  
    logging.info(f"User {current_user.username} logged out at {datetime.now()}")
    return {"message": "Successfully logged out"}