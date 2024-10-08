from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime
from decimal import Decimal

class PaymentMethod(str, Enum):
    COD = "cod"
    ONLINE = "online"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class ChargeResponse(BaseModel):
    amount: Decimal  
    created_at: datetime
    stripe_charge_id: Optional[str] = None

    class Config:
        from_attributes = True  

class SellerInfo(BaseModel):
    seller_name: str
    seller_contact: str
    store_name: str  
    store_location: str 

class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: Decimal 
    seller: SellerInfo

class DeliveryAddress(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str

class OrderCreate(BaseModel):
    payment_method: PaymentMethod  
    delivery_address_index: Optional[int] = None
    coupon_code: Optional[str] = None 
    stripe_token: Optional[str] = None

class OrderResponse(BaseModel):
    order_id: str  
    buyer_name: str  
    items: List[OrderItem]
    total_price: Decimal 
    final_price: Decimal  
    coupon_code: Optional[str] = None
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    delivery_address: DeliveryAddress
    order_date: datetime
    charge: Optional[ChargeResponse] = None

    class Config:
        from_attributes = True  
