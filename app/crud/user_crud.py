from fastapi import HTTPException
from app.models.users import User, Seller, Buyer, Address
from app.schemas.userschema import UserUpdate, UserResponse, SellerResponse, UserCreate, SellerBase, AddressBase, BuyerResponse
from typing import List
from bson import ObjectId
from pymongo import errors

ADMIN_SECRET_CODE = "accesstoadmin"

def get_users():
    users = User.objects.all()
    return [UserResponse(username=user.username, email=user.email, role=user.role, phone_no=user.phone_no) for user in users]

def get_user_by_username(username: str):
    user = User.objects.get(username=username)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

def update_user(username: str, user_update: UserUpdate):
    user = User.objects.get(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")  

    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.phone_no is not None:
        user.phone_no = user_update.phone_no

    user.save()
    user.reload()
    return user

def delete_user(username: str):
    user = User.objects.get(username=username)
    if user:
        user.delete()
        return {"message": f"User {username} and associated profile deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")

def create_seller_profile(user_data):
    seller = Seller(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        phone_no= user_data.phone_no,
        store_name="",  
        store_address=""  
    )
    seller.set_password(user_data.password)
    seller.save()
    return seller


def update_seller(username: str, seller_update: SellerBase):
    seller = Seller.objects.get(username=username)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")

    if seller_update.store_name is not None:
        seller.store_name = seller_update.store_name
    if seller_update.store_address is not None:
        seller.store_address = seller_update.store_address

    seller.save()
    return SellerResponse(
        username=seller.username,
        email=seller.email,
        role=seller.role,
        phone_no=seller.phone_no,
        store_name=seller.store_name,
        store_address=seller.store_address
    )

def create_buyer_profile(user_data):
    buyer = Buyer(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        phone_no= user_data.phone_no,
        addresses=[]  
    )
    buyer.set_password(user_data.password)
    buyer.save()
    return buyer

def add_buyer_addresses(username: str, address_data_list: List[AddressBase]):
    buyer = Buyer.objects.get(username=username)

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    personal_address_exists = any(addr.address_type == "home" for addr in buyer.addresses)

    for address_data in address_data_list:
        if address_data.address_type == "home":
            if personal_address_exists:
                for addr in buyer.addresses:
                    if addr.address_type == "home":
                        addr.address_type = "other"
        new_address = Address(**address_data.model_dump())
        buyer.add_address(new_address)
    buyer.save()
    addresses = [AddressBase(**addr.to_mongo()) for addr in buyer.addresses]
    return BuyerResponse(
            username=buyer.username,
            email=buyer.email,
            full_name=buyer.full_name,
            role=buyer.role,
            phone_no= buyer.phone_no,
            addresses=addresses
        )

def get_all_buyers_with_primary_address():
    buyers = Buyer.objects()  
    buyer_data = []

    for buyer in buyers:
        primary_address = buyer.get_primary_address()
        buyer_data.append({
            "username": buyer.username,
            "email": buyer.email,
            "full_name": buyer.full_name,
            "phone_no": buyer.phone_no,
            "primary_address": primary_address.to_mongo() if primary_address else None
        })

    return buyer_data

def update_buyer_address(username: str, index: int, address_update: AddressBase):
    buyer = Buyer.objects.get(username=username)

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    if index < 0 or index >= len(buyer.addresses):
        raise HTTPException(status_code=404, detail="Address not found at this index")

    address = buyer.addresses[index]

    if address_update.address_line1 is not None:
        address.address_line1 = address_update.address_line1
    if address_update.address_line2 is not None:
        address.address_line2 = address_update.address_line2
    if address_update.city is not None:
        address.city = address_update.city
    if address_update.state is not None:
        address.state = address_update.state
    if address_update.postal_code is not None:
        address.postal_code = address_update.postal_code
    if address_update.country is not None:
        address.country = address_update.country
    if address_update.is_primary is not None:
        address.is_primary = address_update.is_primary
    if address_update.address_type is not None:
        address.address_type = address_update.address_type

    buyer.save()

    addresses = [AddressBase(**addr.to_mongo()) for addr in buyer.addresses]
    return BuyerResponse(
        username=buyer.username,
        email=buyer.email,
        full_name=buyer.full_name,
        role=buyer.role,
        phone_no=buyer.phone_no,
        addresses=addresses
    )

def delete_buyer_address(username: str, index: int):
    buyer = Buyer.objects.get(username=username)
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    if index < 0 or index >= len(buyer.addresses):
        raise HTTPException(status_code=404, detail="Address not found at this index")
    buyer.addresses.pop(index)
    buyer.save()
    return {"detail": "Address successfully deleted"}

def delete_all_addresses(username: str):
    buyer = Buyer.objects.get(username=username)
    
    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")
    buyer.addresses=[]
    buyer.save()
    
    return {"detail": "All addresses successfully deleted"}
