from mongoengine import Document, ReferenceField, IntField, DateTimeField, CASCADE, ListField, EmbeddedDocumentField, EmbeddedDocument
from app.models.users import Buyer
from datetime import datetime
from app.models.products import Product

class CartItem(EmbeddedDocument):
    product = ReferenceField(Product, required=True)
    quantity = IntField(required=True, min_value=1)

class Cart(Document):
    buyer = ReferenceField(Buyer, required=True, reverse_delete_rule=CASCADE)
    items = ListField(EmbeddedDocumentField(CartItem), default=list)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def add_item(self, product: Product, quantity: int = 1):
        for item in self.items:
            if item.product == product:
                item.quantity += quantity
                break
        else:
            new_item = CartItem(product=product, quantity=quantity)
            self.items.append(new_item)
        self.updated_at = datetime.now()
        self.save()

    def remove_item(self, product: Product):
        self.items = [item for item in self.items if item.product != product]
        self.updated_at = datetime.now()
        self.save()

    def clear_cart(self):
        self.items =[]
        self.updated_at = datetime.now()
        self.save()

    def get_total_price(self):
        total = sum(item.product.get_final_price() * item.quantity for item in self.items)
        return total