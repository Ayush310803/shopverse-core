from fastapi import HTTPException
from mongoengine import DoesNotExist
from app.models.users import Buyer
from app.models.products import Product
from app.models.carts import Cart, CartItem
from app.schemas.orderschema import OrderCreate, OrderResponse, OrderItem, DeliveryAddress, SellerInfo, PaymentMethod, PaymentStatus, ChargeResponse
from app.models.coupon import Coupon
from datetime import datetime
from app.models.users import Buyer
from app.models.carts import Cart
from app.models.order import Order, OrderHistory, Charge
from app.utils.invoice import send_low_stock_email
from decimal import Decimal
import stripe
from app.config import settings

stripe.api_key = settings.STRIPE_API_KEY

def create_order_logic(order_data: OrderCreate, current_buyer: Buyer): 
    buyer = current_buyer
    cart = Cart.objects.get(buyer=buyer)

    if not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    if order_data.delivery_address_index is not None:
        if order_data.delivery_address_index < 0 or order_data.delivery_address_index >= len(buyer.addresses):
            raise HTTPException(status_code=404, detail="Delivery address not found")
        delivery_address = buyer.addresses[order_data.delivery_address_index]
    else:
        delivery_address = buyer.get_primary_address()
        if not delivery_address:
            raise HTTPException(status_code=400, detail="No primary address found")

    total_price = cart.get_total_price()

    final_price = total_price
    coupon = None
    if order_data.coupon_code:
        try:
            coupon = Coupon.objects.get(code=order_data.coupon_code)
            if coupon.is_valid_for_buyer(buyer):
                if total_price < coupon.min_order_value:
                    raise HTTPException(status_code=400, detail="Total price is less than minimum order value")
                discount = coupon.apply_discount(total_price)
                final_price = max(Decimal(0), total_price - discount)

                if coupon.is_single_use and buyer not in coupon.used_by:
                    coupon.used_by.append(buyer)
                    coupon.save()
            else:
                raise HTTPException(status_code=400, detail="Coupon is not valid for this buyer or has expired")
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Coupon not found")

    order = Order(
        buyer=buyer,
        items=cart.items,  
        total_price=total_price,
        final_price=final_price,
        payment_method=order_data.payment_method,
        delivery_address=delivery_address,
        coupon=coupon
    )

    if order_data.payment_method == PaymentMethod.ONLINE:
        try:
            charge = stripe.Charge.create(
                amount=int(final_price * 100),  
                currency='inr',
                description=f"Charge for order ID: {str(order.id)}",
                source=order_data.stripe_token,  
            )
            order.payment_status = PaymentStatus.SUCCEEDED
            order.charge = Charge(
                amount=final_price,
                stripe_charge_id=charge.id
            )
        except stripe.error.CardError as e:
            order.payment_status = PaymentStatus.FAILED
            raise HTTPException(status_code=400, detail=f"Stripe Payment Failed: {e.user_message}")
    else:
        order.payment_status = PaymentStatus.PENDING  

    order.save()

    for item in cart.items:
        product = item.product
        try:
            product.reduce_stock(item.quantity)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        if product.stock < 10:
            send_low_stock_email(product.seller.email, product.name)

    OrderHistory(order=order, buyer=buyer).save()

    cart.clear_cart()

    return order

def retrieve_order_history(current_buyer: Buyer):
    order_history = OrderHistory.objects.filter(buyer=current_buyer).all()

    if not order_history:
        raise ValueError("No order history found")

    order_history_response = []  
    
    for history in order_history:
        order = history.order
        
        order_response = OrderResponse(
            order_id=str(order.id),
            buyer_name=current_buyer.full_name,
            items=[
                OrderItem(
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.price,
                    seller=SellerInfo(
                        seller_name=item.product.seller.full_name,
                        seller_contact=item.product.seller.phone_no,
                        store_name=item.product.seller.store_name,
                        store_location=item.product.seller.store_address
                    )
                ) for item in order.items
            ],
            total_price=order.total_price,
            coupon_code= order.coupon.code if order.coupon else None,
            final_price=order.final_price,  
            payment_method=order.payment_method,
            payment_status=order.payment_status,
            delivery_address=DeliveryAddress(
                address_line1=order.delivery_address.address_line1,
                address_line2=order.delivery_address.address_line2,
                city=order.delivery_address.city,
                state=order.delivery_address.state,
                postal_code=order.delivery_address.postal_code,
                country=order.delivery_address.country
            ),
            order_date=order.order_at,
            charge=ChargeResponse(
                amount=order.charge.amount if order.charge else Decimal(0.0),
                stripe_charge_id=order.charge.stripe_charge_id if order.charge else None,
                created_at=order.charge.created_at if order.charge else None,
            ) if order.charge else None
        )

        order_history_response.append(order_response)

    return order_history_response
