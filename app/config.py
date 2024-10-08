from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_hostname: str
    database_port: int
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    debugging: int
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        print(env_file)


settings = Settings()