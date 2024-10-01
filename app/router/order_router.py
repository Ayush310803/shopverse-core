from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from app.crud.order_crud import create_order_logic, retrieve_order_history
from app.schemas.orderschema import OrderCreate, OrderResponse, OrderItem, DeliveryAddress, SellerInfo
from app.dependencies import get_current_user
from app.models.users import Buyer
from typing import List
from app.utils.invoice import send_sms_notification, send_email_with_invoice, generate_invoice_pdf

router = APIRouter()

@router.post("/", response_model=OrderResponse)
async def create_order(order_data: OrderCreate, background_tasks: BackgroundTasks, request: Request, current_buyer: Buyer = Depends(get_current_user)):
    order = create_order_logic(order_data, current_buyer)
    
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
        final_price=order.final_price,
        coupon_code=order_data.coupon_code,  
        payment_method=order_data.payment_method,
        delivery_address=DeliveryAddress(
            address_line1=order.delivery_address.address_line1,
            address_line2=order.delivery_address.address_line2,
            city=order.delivery_address.city,
            state=order.delivery_address.state,
            postal_code=order.delivery_address.postal_code,
            country=order.delivery_address.country
        ),
        order_date=order.order_at
    )
    
    pdf_path = generate_invoice_pdf(order_response)
    background_tasks.add_task(
        send_email_with_invoice,
        to_email=current_buyer.email,
        subject="Your Order Invoice",
        order_data=order_response,
        attachment_path=pdf_path
    )
    background_tasks.add_task(
        send_sms_notification,
        phone_number=current_buyer.phone_no,
        message_body=f"Your order with ID {order.id} has been placed successfully."
    )

    return order_response

@router.get("/order-history/", response_model=List[OrderResponse])
async def get_order_history(current_buyer: Buyer = Depends(get_current_user)):
    order_history_response = retrieve_order_history(current_buyer)
    return order_history_response
        