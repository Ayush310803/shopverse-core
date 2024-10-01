from fastapi import APIRouter, Depends, HTTPException
from app.crud.wishlist_crud import add_to_wishlist, get_wishlist, remove_from_wishlist
from app.schemas.wishlistschema import WishlistItemModel, WishlistResponse
from app.schemas.userschema import UserResponse
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/add", response_model=WishlistResponse)
def add_to_wishlist_route(wishlist_data: WishlistItemModel, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role == "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    wishlist_response = add_to_wishlist(current_user.username, wishlist_data.product_name)
    return wishlist_response

@router.get("/", response_model=WishlistResponse)
def get_wishlist_route(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role == "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    wishlist_response = get_wishlist(current_user.username)
    return wishlist_response

@router.delete("/remove", response_model=WishlistResponse)
def remove_from_wishlist_route(product_name: str, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role == "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    wishlist_response = remove_from_wishlist(current_user.username, product_name)
    return wishlist_response
