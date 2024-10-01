from fastapi import APIRouter, HTTPException, Depends
from app.crud.product_crud import create_brand, get_brands, get_brand, update_brand, delete_brand,create_category, get_category,get_categories, update_category, delete_category,create_product,get_products, get_product, update_product, delete_product, delete_offer_by_name, create_offer, update_offer
from app.schemas.productschema import BrandBase, ProductBase, CategoryBase, BrandResponse, CategoryResponse, ProductResponse, ProductUpdate, OfferBase, OfferResponse, OfferUpdate
from app.schemas.userschema import UserResponse
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/get_all_brands/", response_model=list[BrandResponse])
async def get_brands_endpoint():
    return get_brands()

@router.get("/get_brand/{name}", response_model=BrandResponse)
async def get_brand_endpoint(name: str):
    return get_brand(name)

@router.post("/create_brand/", response_model=BrandResponse)
async def create_brand_endpoint(brand: BrandBase, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return create_brand(brand.name)

@router.put("/Update_brand/{name}", response_model=BrandResponse)
async def update_brand_endpoint(name: str, new_name: str, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return update_brand(name, new_name)

@router.delete("/Delete_brand/{name}")
async def delete_brand_endpoint(name: str, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_brand(name)

@router.get("/get_all_categories/", response_model=list[CategoryResponse])
async def get_all_categories():
    categories = get_categories()  
    result =[{
        "name": category.name,
        "parent_name": category.parent.name if category.parent else None
    } for category in categories ]

    return result

@router.post("/create_category/", response_model=CategoryResponse)
async def create_category_route(category_data: CategoryBase, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    new_category = create_category(category_data)  
    return {
        "name": new_category.name,
        "parent_name": new_category.parent.name if new_category.parent else None
    }

@router.get("/get_category/{name}", response_model=CategoryResponse)
async def get_category_endpoint(name: str):
    category = get_category(name) 
    return {
        "name": category.name,
        "parent_name": category.parent.name if category.parent else None
    }

@router.put("/Update_category/{name}", response_model=CategoryResponse)
async def update_category_endpoint(name: str, new_name: str, parent_name: str = None, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    updated_category = update_category(name, new_name, parent_name) 
    return {
        "name": updated_category.name,
        "parent_name": updated_category.parent.name if updated_category.parent else None
    }

@router.delete("/delete_category/{name}")
async def delete_category_endpoint(name: str, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_category(name)  

@router.get("/get_all_products/", response_model=list[ProductResponse])
async def get_products_endpoint():
    return get_products()

@router.post("/create_product/", response_model=ProductResponse)
async def create_product_endpoint(product: ProductBase, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role not in ["admin", "seller"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    new_product = create_product(product) 

    return ProductResponse(
        name=new_product.name,
        description=new_product.description,
        price=new_product.price,
        stock=new_product.stock,
        category_name=new_product.category.name,  
        brand_name=new_product.brand.name,
        seller_name=new_product.seller.username,
        final_price=new_product.get_final_price(),
        offer_name=new_product.offer.name if new_product.offer else None
    )


@router.get("/get_product/{name}", response_model=ProductResponse)
async def get_product_endpoint(name: str):
    product = get_product(name)

    return ProductResponse(
        name=product.name,
        description=product.description,
        price=product.price,
        stock=product.stock,
        category_name=product.category.name, 
        brand_name=product.brand.name,
        seller_name=product.seller.username,
        final_price=product.get_final_price(),
        offer_name=product.offer.name if product.offer else None
    )

@router.put("/Update_product/{name}", response_model=ProductResponse)
async def update_product_endpoint(name: str, product_update: ProductUpdate, current_user: UserResponse = Depends(get_current_user)):
    product = get_product(name)
    if current_user.role != "admin" and current_user.username!=product.seller_name:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    updated_product = update_product(name, product_update)

    return ProductResponse(
        name=updated_product.name,
        description=updated_product.description,
        price=updated_product.price,
        stock=updated_product.stock,
        category_name=updated_product.category.name, 
        brand_name=updated_product.brand.name,
        seller_name=updated_product.seller.username,
        final_price=updated_product.get_final_price(),
        offer_name=updated_product.offer.name if updated_product.offer else None
    )

@router.delete("/Delete_product/{name}")
async def delete_product_endpoint(name: str, current_user: UserResponse = Depends(get_current_user)):
    product = get_product(name)
    if current_user.role != "admin" and current_user.username!=product.seller_name:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    delete_product(name)
    return {"message": "Product deleted"}

@router.post("/create_offer", response_model=OfferResponse)
async def create_offers(offer: OfferBase, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return create_offer(offer)

@router.put("/Update_offer/{offer_name}", response_model=OfferResponse)
async def update_offer_endpoint(offer_name: str,offer_update: OfferUpdate,current_user: UserResponse = Depends(get_current_user)):

    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_offer = update_offer(offer_name, offer_update)

    return OfferResponse(
        name=updated_offer.name,
        discount_percent=updated_offer.discount_percent,
        start_date=updated_offer.start_date,
        end_date=updated_offer.end_date,
        is_active=updated_offer.is_active
    )

@router.delete("/delete_offer/{name}")
async def delete_offer(offer_name: str, current_user: UserResponse = Depends(get_current_user)):
    if current_user.role != "admin" and "seller":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return delete_offer_by_name(offer_name)