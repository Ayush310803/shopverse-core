from fastapi import HTTPException
from mongoengine import DoesNotExist
from app.models.users import Seller
from app.models.products import Product, Brand, Category, Offer
from app.schemas.productschema import BrandResponse, ProductUpdate, ProductBase, OfferBase, OfferUpdate, ProductResponse

def create_brand(name: str):
    if Brand.objects.filter(name=name).first():
        raise HTTPException(status_code=400, detail="Brand with this name already exists")
    brand = Brand(name=name)
    brand.save()
    return brand

def get_brands():
    brands=Brand.objects.all()
    return brands

def get_brand(name: str):
    try:
        return Brand.objects.get(name=name)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Brand not found")

def update_brand(name: str, new_name: str):
    brand = get_brand(name)
    brand.name = new_name
    brand.save()
    return brand

def delete_brand(name: str):
    brand = get_brand(name)
    brand.delete()
    return {"message": "Brand deleted"}

def create_category(category_data: Category):
    if Category.objects.filter(name=category_data.name).first():
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    parent_category = None
    if category_data.parent_name:
        try:
            parent_category = Category.objects.get(name=category_data.parent_name)
        except Category.DoesNotExist:
            raise HTTPException(status_code=404, detail="Parent category not found")

    new_category = Category(
        name=category_data.name,
        parent=parent_category
    )
    new_category.save()
    return new_category

def get_category(name: str):
    try:
        return Category.objects.get(name=name)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category not found")
    
def get_categories():
    categories = Category.objects.all() 
    return categories

def update_category(name: str, new_name: str, parent_name: str = None):
    category = get_category(name)
    
    parent_category = None
    if parent_name:
        try:
            parent_category = Category.objects.get(name=parent_name)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Parent category not found")
    
    category.name = new_name
    category.parent = parent_category
    category.save()
    return category

def delete_category(name: str):
    category = get_category(name)
    category.delete()
    return {"message": "Category deleted"}

def create_product(product_data: ProductBase):
    try:
        category = Category.objects.get(name=product_data.category_name)
        brand = Brand.objects.get(name=product_data.brand_name)
        seller = Seller.objects.get(username=product_data.seller_name)  
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Category, Brand, or Seller not found")

    offer = None
    if product_data.offer_name:
        try:
            offer = Offer.objects.get(name=product_data.offer_name)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Offer not found")

    product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
        category=category,
        brand=brand,
        seller=seller,  
        offer=offer )
    
    product.save()
    return product

def get_products():
    products=Product.objects.all()
    return [ProductResponse(name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_name=product.category.name, 
        brand_name=product.brand.name,
        seller_name=product.seller.username,
        final_price=product.get_final_price(),
        offer_name=product.offer.name if product.offer else None ) for product in products]
    
def get_product(name: str):
    try:
        return Product.objects.get(name=name)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

def update_product(name: str, product_update: ProductUpdate):
    product = get_product(name)

    if product_update.category_name:
        try:
            category = Category.objects.get(name=product_update.category_name)
            product.category = category
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Category not found")

    if product_update.brand_name:
        try:
            brand = Brand.objects.get(name=product_update.brand_name)
            product.brand = brand
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Brand not found")

    if product_update.name is not None:
        product.name = product_update.name
    if product_update.description is not None:
        product.description = product_update.description
    if product_update.price is not None:
        product.price = product_update.price
    if product_update.stock is not None:
        product.stock = product_update.stock

    if product_update.offer_name is not None:
        try:
            offer = Offer.objects.get(name=product_update.offer_name)
            product.offer = offer
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Offer not found")
    else:
        product.offer = None  
    product.save()
    
    return product

def delete_product(name: str):
    product = get_product(name)
    product.delete()
    return {"message": "Product deleted"}


def create_offer(offer_data: OfferBase):
    existing_offer = Offer.objects.filter(name=offer_data.name).first()

    if existing_offer:
        raise HTTPException(status_code=400, detail="Offer with this name already exists")
    else:
        new_offer = Offer(
            name=offer_data.name,
            discount_percent=offer_data.discount_percent,
            start_date=offer_data.start_date,
            end_date=offer_data.end_date,
            is_active=offer_data.is_active
        )
        new_offer.save()
        return new_offer

def update_offer(offer_name: str, offer_data: OfferUpdate):
    try:
        offer = Offer.objects.get(name=offer_name)  
    except Offer.DoesNotExist:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer_data.name:
        offer.name = offer_data.name
    if offer_data.discount_percent:
        offer.discount_percent = offer_data.discount_percent
    if offer_data.start_date:
        offer.start_date = offer_data.start_date
    if offer_data.end_date:
        offer.end_date = offer_data.end_date
    if offer_data.is_active is not None:
        offer.is_active = offer_data.is_active

    offer.save() 
    return offer

def delete_offer_by_name(offer_name: str):
    offer = Offer.objects.get(name=offer_name)
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    offer.delete()  
    return {"detail": "Offer deleted successfully"}



