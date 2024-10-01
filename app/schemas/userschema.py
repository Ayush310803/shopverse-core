from pydantic import BaseModel, EmailStr
from app.models.users import User
from typing import Optional, List

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    phone_no: Optional[str] = None
    password: str
    full_name: str
    role: Optional[str] = "buyer" 
    secret_code: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone_no: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    email: str
    role: str
    phone_no: Optional[str] = None

    class Config:
        from_attributes = True

class SellerBase(BaseModel):
    store_name: str
    store_address: str

class SellerResponse(UserResponse):
    store_name: str
    store_address: str

    class Config:
        from_attributes = True

class AddressBase(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    is_primary: Optional[bool] = False
    address_type: Optional[str] = "other"

class AddressUpdate(AddressBase):
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_primary: Optional[bool] = None

class BuyerBase(BaseModel):
    addresses: List[AddressBase]

class BuyerResponse(UserResponse):
    addresses: List[AddressBase]

    class Config:
        from_attributes = True

class BuyersResponse(BaseModel):
    username: str
    email: str
    full_name: str
    primary_address: dict