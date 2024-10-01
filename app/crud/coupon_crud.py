from fastapi import HTTPException
from mongoengine.errors import NotUniqueError, DoesNotExist
from app.models.coupon import Coupon  
from app.schemas.couponschema import CreateCoupon, UpdateCoupon, CouponResponse

def get_coupons():
    coupons = Coupon.objects.all()
    return [
        CouponResponse(
            code=coupon.code,
            discount_percentage=coupon.discount_percentage,
            max_discount_amount=coupon.max_discount_amount,
            min_order_value=coupon.min_order_value,
            is_single_use=coupon.is_single_use,
            expiration_date=coupon.expiration_date,
            used_by=[buyer.username for buyer in coupon.used_by]  
        )
        for coupon in coupons
    ]
    
def create_coupon(coupon_data: CreateCoupon):
    try:
        coupon = Coupon(
            code=coupon_data.code,
            discount_percentage=coupon_data.discount_percentage,
            max_discount_amount=coupon_data.max_discount_amount,
            min_order_value=coupon_data.min_order_value,
            is_single_use=coupon_data.is_single_use,
            expiration_date=coupon_data.expiration_date
        )
        coupon.save()
        return CouponResponse(
            code=coupon.code,
            #applicable_for=[buyer.username for buyer in coupon.applicable_for],
            discount_percentage=coupon.discount_percentage,
            max_discount_amount=coupon.max_discount_amount,
            min_order_value=coupon.min_order_value,
            is_single_use=coupon.is_single_use,
            expiration_date=coupon.expiration_date,
            used_by=[buyer.username for buyer in coupon.used_by]  
        )
    except NotUniqueError:
        raise HTTPException(status_code=400, detail="Coupon code must be unique")

def get_coupon(code: str):
    try:
        coupon = Coupon.objects.get(code=code)
        return CouponResponse(
            code=coupon.code,
            #applicable_for=[buyer.username for buyer in coupon.applicable_for],
            discount_percentage=coupon.discount_percentage,
            max_discount_amount=coupon.max_discount_amount,
            min_order_value=coupon.min_order_value,
            is_single_use=coupon.is_single_use,
            expiration_date=coupon.expiration_date,
            used_by=[buyer.username for buyer in coupon.used_by]  
        )
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Coupon not found")

def update_coupon(code: str, update_data: UpdateCoupon):
    try:
        coupon = Coupon.objects.get(code=code)

        if update_data.discount_percentage is not None:
            coupon.discount_percentage = update_data.discount_percentage
        if update_data.max_discount_amount is not None:
            coupon.max_discount_amount = update_data.max_discount_amount
        if update_data.min_order_value is not None:
            coupon.min_order_value = update_data.min_order_value
        if update_data.expiration_date is not None:
            coupon.expiration_date = update_data.expiration_date

        coupon.save()
        return CouponResponse(
            code=coupon.code,
            #applicable_for=[buyer.username for buyer in coupon.applicable_for],
            discount_percentage=coupon.discount_percentage,
            max_discount_amount=coupon.max_discount_amount,
            min_order_value=coupon.min_order_value,
            is_single_use=coupon.is_single_use,
            expiration_date=coupon.expiration_date,
            used_by=[buyer.username for buyer in coupon.used_by]  
        )

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Coupon not found")

def delete_coupon(code: str):
    try:
        coupon = Coupon.objects.get(code=code)
        coupon.delete()
        return {"message": "Coupon deleted successfully"}
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Coupon not found")
