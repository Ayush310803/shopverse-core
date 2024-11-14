from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from app.crud.order_crud import create_order_logic, retrieve_order_history
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.models.order import Order
from app.schemas.orderschema import OrderCreate, OrderResponse, OrderItem, DeliveryAddress, SellerInfo, ChargeResponse, PaymentMethod, PaymentStatus
from app.dependencies import get_current_user
from app.models.users import Buyer
from typing import List
from app.utils.invoice import send_sms_notification, send_email_with_invoice, generate_invoice_pdf
import stripe
from app.config import settings
from decimal import Decimal

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
stripe.api_key= settings.STRIPE_API_KEY

@router.post("/")
async def create_order(order_data: OrderCreate, background_tasks: BackgroundTasks, request: Request, current_buyer: Buyer = Depends(get_current_user)):
    order = await create_order_logic(order_data, current_buyer)
    
    if order_data.payment_method == PaymentMethod.COD:
        pdf_path = generate_invoice_pdf(order)
        background_tasks.add_task(
            send_email_with_invoice,
            to_email=current_buyer.email,
            subject="Your Order Invoice",
            order_data=order,
            attachment_path=pdf_path
        )
        background_tasks.add_task(
            send_sms_notification,
            phone_number=current_buyer.phone_no,
            message_body=f"Your order with ID {order.order_id} has been placed successfully."
        )

    return order

@router.get("/order-history/", response_model=List[OrderResponse])
async def get_order_history(current_buyer: Buyer = Depends(get_current_user)):
    order_history_response = retrieve_order_history(current_buyer)
    return order_history_response

@router.get("/payment-success", response_class=HTMLResponse)
async def payment_success(request: Request, session_id: str, background_tasks: BackgroundTasks):
    checkout_session = stripe.checkout.Session.retrieve(session_id)

    if not checkout_session:
        raise HTTPException(status_code=404, detail="Invalid session ID")
    order = Order.objects.filter(charge__stripe_checkout_id=session_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.payment_status == PaymentStatus.SUCCEEDED:
        raise HTTPException(status_code=400, detail=" Already Payment Succeeded")

    if checkout_session.payment_status == "paid":
        order.payment_status = PaymentStatus.SUCCEEDED
        order.save()
    else:
        raise HTTPException(status_code=400, detail="Payment not confirmed")
    
    if order.payment_method == PaymentMethod.ONLINE:
        order_response = OrderResponse(
        order_id=str(order.id),
        buyer_name=order.buyer.full_name,
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
        coupon_code=order.coupon.code if order.coupon else None,  
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
        pdf_path = generate_invoice_pdf(order_response)
        background_tasks.add_task(
            send_email_with_invoice,
            to_email=order.buyer.email,
            subject="Your Order Invoice",
            order_data=order_response,
            attachment_path=pdf_path
        )
        background_tasks.add_task(
            send_sms_notification,
            phone_number=order.buyer.phone_no,
            message_body=f"Your order with ID {order.id} has been placed successfully."
        )

    return templates.TemplateResponse("payment_success.html", {
        "request": request,
        "order": order,
        "session_id": session_id
    })
  