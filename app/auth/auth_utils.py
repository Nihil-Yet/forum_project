# установленные модули
import bcrypt
import jwt
from datetime import timedelta, datetime
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# собственные модули
from settings.config import appSettings

# хэширование пароля
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# проверка пароля
def check_password(stored_hash: str, password: str) -> bool:
    stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

# создание токена
def encode_JWT(
        payload: dict, 
        private_key: str = appSettings.authJWT.private_key_path.read_text(), 
        alg: str = appSettings.authJWT.algorithm,
        expire_timedelta: timedelta | None = None,
        expire_minutes: int = appSettings.authJWT.access_token_expire_minutes,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes = expire_minutes)
    to_encode.update(
        iat = now,
        exp = expire,
        )
    encoded = jwt.encode(to_encode, private_key, algorithm=alg,)
    return encoded

# декодирование токена
def decode_JWT(
        token: str | bytes, 
        public_key: str = appSettings.authJWT.public_key_path.read_text(), 
        alg: str = appSettings.authJWT.algorithm
):
    try:
        decoded = jwt.decode(token, public_key, algorithms=[alg])
        return decoded
    except jwt.InvalidTokenError as ex:
        logging.error(f"{ex}")
        raise HTTPException(status_code=401, detail="Invalid token error")

http_bearer = HTTPBearer()
# получение значений токена
def get_jwt_payload(
        credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    token = credentials.credentials
    payload = decode_JWT(token=token)
    return payload
