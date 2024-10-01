from fastapi import APIRouter, HTTPException, Depends
from app.crud.cart_crud import add_to_cart,remove_from_cart,update_cart_item, get_cart
from app.schemas.userschema import UserResponse
from app.schemas.cartschema import CartItemModel, CartItemUpdate, CartResponse
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/add", response_model=CartResponse)
def add_to_cart_route(cart_data: CartItemModel, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role == "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    cart_response = add_to_cart(current_user.username, cart_data.product_name, cart_data.quantity)
    return cart_response

@router.get("/", response_model=CartResponse)
def get_cart_route(current_user: UserResponse = Depends(get_current_user)):
    if current_user.role == "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    cart_response = get_cart(current_user.username)
    return cart_response

@router.put("/update", response_model=CartResponse)
def update_cart_route(cart_data: CartItemUpdate, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role == "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    cart_response = update_cart_item(current_user.username, cart_data.product_name, cart_data.quantity)
    return cart_response

@router.delete("/remove", response_model=CartResponse)
def remove_from_cart_route(product_name: str, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role == "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    cart_response = remove_from_cart(current_user.username, product_name)
    return cart_response
