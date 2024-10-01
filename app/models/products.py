from mongoengine import Document, StringField, ReferenceField, DecimalField, IntField, DateTimeField,BooleanField, CASCADE, ListField, EmbeddedDocumentField, EmbeddedDocument
from app.models.users import Seller, Buyer
from datetime import datetime

class Category(Document):
    name = StringField(required=True, unique=True, max_length=50)
    parent = ReferenceField('self', default=None)  

    def __str__(self):
        if self.parent:
            return f"{self.name} (SubCategory of {self.parent.name})"
        return self.name

class Brand(Document):
    name = StringField(required=True, unique=True, max_length=50)

    def __str__(self):
        return self.name

class Offer(Document):
    name = StringField(required=True, max_length=100)
    discount_percent = DecimalField(required=True, precision=2, min_value=0, max_value=100)
    start_date = DateTimeField(required=True)
    end_date = DateTimeField(required=True)
    is_active = BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.discount_percent}% off"

class Product(Document):
    name = StringField(required=True, max_length=100)
    description = StringField()
    price = DecimalField(required=True, precision=2)
    stock = IntField(required=True, min_value=0)
    category = ReferenceField(Category, required=True, reverse_delete_rule=CASCADE)  
    brand = ReferenceField(Brand, required=True, reverse_delete_rule=CASCADE)  
    seller = ReferenceField(Seller, required=True, reverse_delete_rule=CASCADE)  
    offer = ReferenceField(Offer, default=None, reverse_delete_rule=CASCADE)  

    def get_final_price(self):
        if self.offer and self.offer.is_active:
            if self.offer.start_date<datetime.now()<self.offer.end_date:
                return self.price - (self.price * self.offer.discount_percent / 100)
        return self.price
    
    def reduce_stock(self, quantity: int):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
        else:
            raise ValueError("Not enough stock available.")

    def __str__(self):
        return self.name
    

# class Sales(Document):
#     product = ReferenceField(Product, required=True, reverse_delete_rule=CASCADE)
#     seller = ReferenceField(Seller, required=True, reverse_delete_rule=CASCADE)
#     quantity_sold = IntField(required=True, min_value=1)
#     sale_price = DecimalField(required=True, precision=2)
#     sale_date = DateTimeField(default=datetime.now)
#     end_date = DateTimeField(required=True)

#     def __str__(self):
#         return f"Sale of {self.product.name} by {self.seller.store_name}"

#     def save(self, *args, **kwargs):
#         if self.product.stock < self.quantity_sold:
#             raise ValueError(f"Not enough stock for {self.product.name}")
    
#         self.product.stock -= self.quantity_sold
#         self.product.save()  
#         super(Sales, self).save(*args, **kwargs)
    

