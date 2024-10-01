from pydantic import BaseModel,Field
from typing import Optional, List
from enum import Enum
from datetime import datetime

class PaymentMethod(str, Enum):
    COD = "cod"
    ONLINE = "online"

class SellerInfo(BaseModel):
    seller_name: str
    seller_contact: str
    store_name: str  
    store_location: str 

class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float
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

class OrderResponse(BaseModel):
    order_id: str 
    buyer_name: str
    items: List[OrderItem]
    total_price: float
    final_price: float
    coupon_code: Optional[str]=None
    payment_method: str
    delivery_address: DeliveryAddress
    order_date: datetime

    class Config:
        from_attributes = True