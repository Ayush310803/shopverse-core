from pydantic import BaseModel
from typing import List

class WishlistItemModel(BaseModel):
    product_name: str

class WishlistResponse(BaseModel):
    buyer_name: str
    items: List[WishlistItemModel]
