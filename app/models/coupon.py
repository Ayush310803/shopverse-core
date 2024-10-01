from mongoengine import Document, StringField, DecimalField, DateTimeField, ListField, ReferenceField, BooleanField, CASCADE
from app.models.users import Buyer
from datetime import datetime

class Coupon(Document):
    code = StringField(required=True, unique=True) 
    #applicable_for= ListField(ReferenceField(Buyer), default=[]) 
    discount_percentage = DecimalField(required=True, precision=2)  
    max_discount_amount = DecimalField(required=True, precision=2)  
    min_order_value = DecimalField(required=True, precision=2)  
    is_single_use = BooleanField(default=False) 
    used_by = ListField(ReferenceField(Buyer), default=[]) 
    expiration_date = DateTimeField()  

    def is_valid_for_buyer(self, buyer):
        if self.is_single_use and buyer in self.used_by:
            return False  
        
        if self.expiration_date < datetime.now():
            return False  
        
        return True

    def apply_discount(self, order_value):
        if order_value < self.min_order_value:
            return 0  
        
        discount = (order_value * (self.discount_percentage / 100))
        
        return min(discount, self.max_discount_amount)
