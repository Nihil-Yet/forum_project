# установленные модули
from pydantic import BaseModel
from pathlib import Path
import os

# путь к main/
BASE_DIR = Path(__file__).parent.parent


# настройки для создания БД
class DBSettings(BaseModel):
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", 3306))
    user: str = os.getenv("DB_USER", "data_admin")
    password: str = os.getenv("DB_PASSWORD", "data_admin")
    name: str = os.getenv("DB_NAME", "db_forum")


# настройки для создания токена
class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60


# Общие настройки приложения
class AppSettings(BaseModel):
    dbSettings: DBSettings = DBSettings()
    authJWT: AuthJWT = AuthJWT()


appSettings = AppSettings()
