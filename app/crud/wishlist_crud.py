from fastapi import HTTPException
from mongoengine import DoesNotExist
from app.models.users import Buyer
from app.models.products import Product
from app.models.wishlists import Wishlist
from app.schemas.wishlistschema import WishlistItemModel, WishlistResponse

def add_to_wishlist(username: str, product_name: str):
    try:
        product = Product.objects.get(name=product_name)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")
    
    buyer = Buyer.objects.get(username=username)
    
    wishlist = Wishlist.objects.filter(buyer=buyer).first()
    if not wishlist:
        wishlist = Wishlist(buyer=buyer)
        wishlist.save()

    wishlist.add_item(product)
    wishlist.save()

    return WishlistResponse(
        buyer_name=buyer.username,
        items=[WishlistItemModel(product_name=item.name) for item in wishlist.items]
    )

def get_wishlist(username: str):
    buyer = Buyer.objects.get(username=username)
    wishlist = Wishlist.objects.filter(buyer=buyer).first()

    if not wishlist:
        return WishlistResponse(buyer_name=buyer.username, items=[])

    return WishlistResponse(
        buyer_name=buyer.username,
        items=[WishlistItemModel(product_name=item.name) for item in wishlist.items]
    )

def remove_from_wishlist(username: str, product_name: str):
    buyer = Buyer.objects.get(username=username)
    wishlist = Wishlist.objects.filter(buyer=buyer).first()

    if not wishlist:
        raise HTTPException(status_code=404, detail="Wishlist not found")

    try:
        product = Product.objects.get(name=product_name)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

    wishlist.remove_item(product)
    wishlist.save()

    return WishlistResponse(
        buyer_name=buyer.username,
        items=[WishlistItemModel(product_name=item.product.name) for item in wishlist.items]
    )
