from fastapi import APIRouter, HTTPException, Depends
from app.dependencies import get_current_user
from typing import List
import logging
from app.schemas.userschema import UserCreate,User, UserResponse, UserUpdate, SellerBase,SellerResponse, BuyersResponse, BuyerResponse, AddressBase, AddressUpdate
from app.crud.user_crud import update_user, delete_user, get_users, get_user_by_username, update_seller, add_buyer_addresses, update_buyer_address, delete_buyer_address,delete_all_addresses, get_all_buyers_with_primary_address

router = APIRouter()
logging.basicConfig(filename="login_activity.log", level=logging.INFO, format="%(levelname)s - %(message)s",)

@router.get("/get_all_users", response_model=list[UserResponse])
async def read_users():
    return get_users()

@router.get("/get_user/{username}", response_model=UserResponse)
async def read_user(username: str):
    return get_user_by_username(username)
    
@router.get("/get_current_user/", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.put("/update_userdetails/{username}/", response_model=UserResponse)
async def update_user_info(username: str, user_update: UserUpdate, current_user: UserResponse = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        logging.warning(f"User {current_user.username} attempted unauthorized update")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_user = update_user(username, user_update)
    logging.info(f"User {username} updated by {current_user.username}")
    return updated_user

@router.put("/add_and_update-sellerstoredetails/{username}", response_model=SellerResponse)
async def update_seller_endpoint(username: str, seller_update: SellerBase, current_user: UserResponse = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        logging.warning(f"User {current_user.username} attempted unauthorized action")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_seller(username, seller_update)

@router.put("/buyers_add_addresses/{username}", response_model=BuyerResponse)
async def add_buyer_addresses_endpoint(username: str, address_data_list: List[AddressBase], current_user: UserResponse = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        logging.warning(f"User {current_user.username} attempted unauthorized action")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return add_buyer_addresses(username, address_data_list)

@router.put("/buyers_addresses/{username}/addresses/{index}", response_model=BuyerResponse)
async def update_address_router(username: str, index: int, address_data: AddressUpdate,  current_user: UserResponse = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        logging.warning(f"User {current_user.username} attempted unauthorized action")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_buyer_address(username, index, address_data)

@router.delete("/buyers/{username}/addresses/{index}")
async def delete_address_router(username: str, index: int, current_user: UserResponse = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        logging.warning(f"User {current_user.username} attempted unauthorized action")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_buyer_address(username, index)

@router.delete("/buyers/{username}/delete_addresses")
async def delete_all_buyer_addresses(username: str,  current_user: UserResponse = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        logging.warning(f"User {current_user.username} attempted unauthorized action")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_all_addresses(username)
    
@router.delete("/delete_user/{username}")
async def delete_user_route(username: str, current_user: UserResponse = Depends(get_current_user)):
    if current_user.username != username and current_user.role != "admin":
        logging.warning(f"User {current_user.username} attempted unauthorized delete")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    deleted_user = delete_user(username)
    return {"message": "User deleted successfully", "user": deleted_user}

@router.get("/get_all_buyers_with_primary_address", response_model=List[BuyersResponse])
async def get_buyers_with_primary_address():
    buyers = get_all_buyers_with_primary_address()  
    return buyers