from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime

class BrandBase(BaseModel):
    name: str

class BrandResponse(BaseModel):
    name: str

    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    parent_name: Optional[str] = None

class CategoryResponse(BaseModel):
    name: str
    parent_name: Optional[str] = None

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_name: str
    brand_name: str
    seller_name: str 
    offer_name: Optional[str] = None  
    
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_name: Optional[str] = None
    brand_name: Optional[str] = None
    offer_name: Optional[str] = None

class ProductResponse(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    category_name: str
    brand_name: str
    seller_name: str
    final_price: float 
    offer_name: Optional[str] = None

    class Config:
        from_attributes = True


class OfferBase(BaseModel):
    name: str
    discount_percent: float= Field(0.0, ge=0, le=100)
    start_date: datetime
    end_date: datetime
    is_active: Optional[bool] = True

class OfferUpdate(BaseModel):
    name: Optional[str]=None
    discount_percent: Optional[float] = Field(0.0, ge=0, le=100)
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: Optional[bool] = True

class OfferResponse(BaseModel):
    name: str
    discount_percent: float
    start_date: datetime
    end_date: datetime

class SalesBase(BaseModel):
    product_name: str
    seller_name: str
    quantity_sold: int
    sale_price: float
    sale_date: Optional[datetime] = datetime.now()

class SalesResponse(BaseModel):
    product_name: str
    seller_name: str
    quantity_sold: int
    sale_price: float
    sale_date: datetime

    class Config:
        from_attributes = True

class CartItemModel(BaseModel):
    product_name: str
    quantity: int

class CartItemUpdate(BaseModel):
    product_name: Optional[str]= None
    quantity: Optional[int]= 1

class CartModel(BaseModel):
    buyer_name: str
    items: list[CartItemModel]
