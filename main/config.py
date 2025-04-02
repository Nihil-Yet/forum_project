from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parent

class DBSettings(BaseModel):
    host: str = "localhost"
    port: int = 3306
    user: str = "admin"
    password: str = "Mh8-9q-1#U?Jlei_NvSL!p"
    name: str = "db_forum"

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 120
auth_jwt = AuthJWT()

# нахер я это сделал???
class AppSettings(BaseModel):
    dbSettings: DBSettings = DBSettings()
    authJWT: AuthJWT = AuthJWT()

appSettings = AppSettings()