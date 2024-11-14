from pydantic import BaseModel,Field
from typing import Optional, List

class CartItemModel(BaseModel):
    product_name: str
    quantity: int = 1

class CartItemUpdate(BaseModel):
    product_name: Optional[str]= None
    quantity: Optional[int]= 1

class CartModel(BaseModel):
    buyer_name: str
    items: list[CartItemModel]

class CartResponse(BaseModel):
    buyer_name: str
    items: List[CartItemModel]
    total_price: float