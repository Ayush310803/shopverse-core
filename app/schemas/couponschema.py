from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.userschema import BuyerResponse  

class CouponBase(BaseModel):
    discount_percentage: float = Field(0.0, ge=0, le=100, description="Discount percentage for the coupon")
    max_discount_amount: float = Field(0.0, description="Maximum discount amount allowed")
    min_order_value: float = Field(0.0, description="Minimum order value required to apply the coupon")
    is_single_use: bool = Field(default=False, description="Is the coupon single use")
    expiration_date: Optional[datetime] = Field(None, description="Expiration date for the coupon")

class CreateCoupon(CouponBase):
    code: str = Field(..., description="Unique coupon code")

class UpdateCoupon(CouponBase):
    discount_percentage: Optional[float] = Field(0.0, ge=0, le=100, description="Discount percentage for the coupon")
    max_discount_amount: Optional[float] = None
    min_order_value: Optional[float] = None
    expiration_date: Optional[datetime] = None

class CouponResponse(CouponBase):
    code: str = Field(..., description="Unique coupon code")
    #applicable_for: List[str] = Field(default=[], description="List of buyers who can use this coupon")
    used_by: List[str] = Field(default=[], description="List of buyers who have used the coupon")

    class Config:
        from_attributes = True
