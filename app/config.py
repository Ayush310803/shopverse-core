from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    USERNAME: str
    PASSWORD: str
    ACCOUNT_SID: str
    AUTH_TOKEN: str
    PHONE_NO: str
    SENDER_EMAIL: str
    EMAIL_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    STRIPE_API_KEY: str
    PUBLISH_API_KEY: str


    class Config:
        env_file = ".env"
        #print(env_file)


settings = Settings()