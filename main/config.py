from pydantic import BaseModel
from pathlib import Path

BASE_DIR = Path(__file__).parent

host = "localhost"
db_user = "admin"
db_password = "Mh8-9q-1#U?Jlei_NvSL!p"
db_name = "db_forum"

class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"