from fastapi import APIRouter, Depends, HTTPException
from app.schemas.couponschema import CreateCoupon, UpdateCoupon, CouponResponse
from app.schemas.userschema import UserResponse
from app.dependencies import get_current_user
from app.crud.coupon_crud import create_coupon, get_coupon, update_coupon, delete_coupon, get_coupons
from typing import List

router = APIRouter()

@router.get("/", response_model=List[CouponResponse])
async def get_coupons_route():
    return get_coupons()

@router.post("/create/", response_model=CouponResponse)
async def create_coupon_route(coupon_data: CreateCoupon, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return create_coupon(coupon_data)

@router.get("/{code}", response_model=CouponResponse)
async def get_coupon_route(code: str):
    return get_coupon(code)

@router.put("/update/{code}", response_model=CouponResponse)
async def update_coupon_route(code: str, update_data: UpdateCoupon, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_coupon(code, update_data)

@router.delete("/delete/{code}", response_model=dict)
async def delete_coupon_route(code: str, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_coupon(code)
