from mongoengine import Document, ReferenceField, DecimalField, StringField, DateTimeField, CASCADE, ListField, EmbeddedDocumentField
from app.models.users import Buyer, Address
from app.models.carts import CartItem
from app.models.coupon import Coupon
from datetime import datetime


class Order(Document):
    buyer = ReferenceField(Buyer, required=True, reverse_delete_rule=CASCADE)
    items = ListField(EmbeddedDocumentField(CartItem), required=True)  
    total_price = DecimalField(required=True, precision=2)
    final_price = DecimalField(required=True, precision=2, default=0.00)  
    payment_method = StringField(choices=["cod", "online"], required=True)
    delivery_address = EmbeddedDocumentField(Address, required=True)  
    order_at = DateTimeField(default=datetime.now)
    coupon = ReferenceField(Coupon, null=True)  

    def apply_coupon(self, coupon):
        if coupon.is_valid_for_buyer(self.buyer):
            discount = coupon.apply_discount(self.total_price)  
            self.coupon = coupon  
            self.final_price = self.total_price - discount  
            self.final_price = max(0, self.final_price)  
            
            if coupon.is_single_use:
                coupon.used_by.append(self.buyer)  
                coupon.save()
        else:
            raise ValueError("Coupon is not valid for this buyer or has expired.")

    def save(self, *args, **kwargs):
        if self.final_price == 0:  
            self.final_price = self.total_price
        super(Order, self).save(*args, **kwargs)

class OrderHistory(Document):
    order = ReferenceField(Order, required=True, reverse_delete_rule=CASCADE)
    buyer = ReferenceField(Buyer, required=True, reverse_delete_rule=CASCADE)
    created_at = DateTimeField(default=datetime.now)

    def __str__(self):
        return f"Order History for {self.buyer.username} - Order ID: {self.order.id}"
