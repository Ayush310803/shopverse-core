from mongoengine import Document, StringField, EmailField, BooleanField, DateTimeField, EmbeddedDocument, EmbeddedDocumentField, ListField
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Address(EmbeddedDocument):
    address_line1 = StringField(required=True)
    address_line2 = StringField()
    city = StringField(required=True)
    state = StringField(required=True)
    postal_code = StringField(required=True)
    country = StringField(required=True)
    is_primary = BooleanField(default=False)  
    address_type = StringField(choices=["home", "other"], default="other")

class User(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    phone_no = StringField()
    hashed_password = StringField(required=True)
    full_name = StringField(required=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    role = StringField(choices=["admin", "seller", "buyer"], default="buyer")

    meta = {
        'collection': 'users', 
        'allow_inheritance': True 
    }

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)

    def set_password(self, password: str) -> None:
        self.hashed_password = pwd_context.hash(password)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()  
        return super(User, self).save(*args, **kwargs)

class Seller(User):
    store_name = StringField(default="")
    store_address = StringField(default="")

    def __str__(self):
        return self.store_name or "No Store Name"

class Buyer(User):
    addresses = ListField(EmbeddedDocumentField(Address))

    def add_address(self, address: Address):
        if address.is_primary:
            for addr in self.addresses:
                if addr.is_primary:
                    addr.is_primary = False
        self.addresses.append(address)
        self.save()

    def get_primary_address(self):
        for address in self.addresses:
            if address.is_primary:
                return address
        return None

class Admin(User):
    pass
