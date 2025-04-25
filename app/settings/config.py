# установленные модули
from pydantic import BaseModel
from pathlib import Path
import socket

# путь к main/
BASE_DIR = Path(__file__).parent.parent

def is_host_reachable(host):
    try:
        socket.gethostbyname(host)
        return True
    except socket.error:
        return False

# настройки для создания БД
class DBSettings(BaseModel):
    host: str = "db-forum-server" if is_host_reachable("db-forum-server") else "localhost"
    port: int = 3306
    user: str = "data_admin"
    password: str = "data_admin"
    name: str = "db_forum"

# настройки для создания токена
class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "auth" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 60

# Общие настройки приложения
# нахер я это сделал???
class AppSettings(BaseModel):
    dbSettings: DBSettings = DBSettings()
    authJWT: AuthJWT = AuthJWT()
appSettings = AppSettings()