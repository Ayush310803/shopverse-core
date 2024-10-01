from fastapi import FastAPI
from app.router import product_router, user_router, user_auth, cart_router, wishlist_router, order_router, coupon_router
from mongoengine import connect, disconnect
from urllib.parse import quote_plus
import logging
from fastapi.staticfiles import StaticFiles
from app.config import settings

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

username = quote_plus(settings.USERNAME)
password = quote_plus(settings.PASSWORD)
connection_string = f"mongodb+srv://{username}:{password}@cluster0.top9b.mongodb.net/?retryWrites=true&w=majority"

@app.on_event("startup")
async def startup_db_client():
    logging.info("Connecting to MongoDB...")
    connect(db='test_db', host=connection_string)
    logging.info("MongoDB connected.")

@app.on_event("shutdown")
async def shutdown_db_client():
    logging.info("Disconnecting from MongoDB...")
    disconnect()
    logging.info("MongoDB disconnected.")


app.include_router(user_auth.router,  prefix="/api/v1/auth", tags=["auth"])
app.include_router(user_router.router,  prefix="/api/v1", tags=["user"])
app.include_router(product_router.router, prefix="/api/v1/product", tags=["product"])
app.include_router(wishlist_router.router, prefix="/api/v1/wishlist", tags=["wishlist"])
app.include_router(cart_router.router, prefix="/api/v1/cart", tags=["cart"])
app.include_router(coupon_router.router, prefix="/api/v1/coupon", tags=["coupon"])
app.include_router(order_router.router, prefix="/api/v1/order", tags=["order"])
