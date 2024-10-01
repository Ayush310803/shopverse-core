from mongoengine import Document, ReferenceField, CASCADE, ListField
from app.models.users import Buyer
from app.models.products import Product

class Wishlist(Document):
    buyer = ReferenceField(Buyer, required=True, reverse_delete_rule=CASCADE)
    items = ListField(ReferenceField(Product), default=list)

    def add_item(self, product: Product):
        if product not in self.items:
            self.items.append(product)
            self.save()

    def remove_item(self, product: Product):
        if product in self.items:
            self.items.remove(product)
            self.save()