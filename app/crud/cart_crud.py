from fastapi import HTTPException
from mongoengine import DoesNotExist
from app.models.users import Buyer
from app.models.products import Product
from app.models.carts import Cart, CartItem
from app.schemas.cartschema import CartItemModel, CartItemUpdate, CartModel, CartResponse
from datetime import datetime

def add_to_cart(username: str, product_name: str, quantity: int):
    buyer = Buyer.objects.get(username=username)

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    try:
        product = Product.objects.get(name=product_name)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

    if quantity > product.stock:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    cart = Cart.objects.filter(buyer=buyer).first() or Cart(buyer=buyer)
    
    for item in cart.items:
        if item.product == product:
            item.quantity += quantity
            break
    else:
        new_item = CartItem(product=product, quantity=quantity)
        cart.items.append(new_item)

    cart.updated_at = datetime.now()
    cart.save()

    cart_items = [CartItemModel(product_name=item.product.name, quantity=item.quantity) for item in cart.items]
    total_price = cart.get_total_price()

    return CartResponse(buyer_name=buyer.username, items=cart_items, total_price=total_price)


def get_cart(username: str):
    buyer = Buyer.objects.get(username=username)

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    cart = Cart.objects.filter(buyer=buyer).first()

    if not cart:
        cart = Cart(buyer=buyer)
        cart.save()

    cart_items = [CartItemModel(product_name=item.product.name, quantity=item.quantity) for item in cart.items]
    total_price = cart.get_total_price()

    return CartResponse(buyer_name=buyer.username, items=cart_items, total_price=total_price)


def update_cart_item(username: str, product_name: str, quantity: int):
    buyer = Buyer.objects.get(username=username)

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    try:
        product = Product.objects.get(name=product_name)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = Cart.objects.get(buyer=buyer)

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    for item in cart.items:
        if item.product == product:
            if quantity > product.stock:
                raise HTTPException(status_code=400, detail="Not enough stock available")
            item.quantity = quantity
            break
    else:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    cart.updated_at = datetime.now()
    cart.save()

    cart_items = [CartItemModel(product_name=item.product.name, quantity=item.quantity) for item in cart.items]
    total_price = cart.get_total_price()

    return CartResponse(buyer_name=buyer.username, items=cart_items, total_price=total_price)

def remove_from_cart(username: str, product_name: str):
    buyer = Buyer.objects.get(username=username)

    if not buyer:
        raise HTTPException(status_code=404, detail="Buyer not found")

    try:
        product = Product.objects.get(name=product_name)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = Cart.objects.get(buyer=buyer)

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart.items = [item for item in cart.items if item.product != product]

    cart.updated_at = datetime.now()
    cart.save()

    cart_items = [CartItemModel(product_name=item.product.name, quantity=item.quantity) for item in cart.items]
    total_price = cart.get_total_price()

    return CartResponse(buyer_name=buyer.username, items=cart_items, total_price=total_price)
