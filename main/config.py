from pydantic import BaseModel
from pathlib import Path

# путь к main/
BASE_DIR = Path(__file__).parent

# настройки для создания БД
class DBSettings(BaseModel):
    host: str = "localhost"
    port: int = 3306
    user: str = "admin"
    password: str = "admin"
    name: str = "db_forum"

# настройки для создания токена
class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60
auth_jwt = AuthJWT()

# Общие настройки приложения
# нахер я это сделал???
class AppSettings(BaseModel):
    dbSettings: DBSettings = DBSettings()
    authJWT: AuthJWT = AuthJWT()
appSettings = AppSettings()