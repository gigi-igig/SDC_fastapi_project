from pydantic_settings import BaseSettings, SettingsConfigDict

class __Settings(BaseSettings):
    host: str = ""
    port: str = ""

    postgres_user: str = ""
    postgres_password: str = ""
    postgres_db: str = ""
    postgres_host: str = ""
    postgres_port: int = 5432

    test_postgres_user: str = ""
    test_postgres_password: str = ""
    test_postgres_db: str = ""
    test_postgres_host: str = ""
    test_postgres_port: int = 5432

    token_secret_key: str = ""
    token_algorithm: str = ""
    access_token_expire_minutes: int = 30

    model_config = SettingsConfigDict(env_file=".env")

settings = __Settings()