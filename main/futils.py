import bcrypt
import jwt
from datetime import timedelta, datetime

from config import auth_jwt

# Хэширование пароля
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

# Проверка пароля
def check_password(stored_hash: str, password: str) -> bool:
    stored_hash = stored_hash.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)

def encode_JWT(
        payload: dict, 
        private_key: str = auth_jwt.private_key_path.read_text(), 
        alg: str = auth_jwt.algorithm,
        expire_timedelta: timedelta | None = None,
        expire_minutes: int = auth_jwt.access_token_expire_minutes,
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

def decode_JWT(
        token: str | bytes, 
        public_key: str = auth_jwt.public_key_path.read_text(), 
        algorithm: str = auth_jwt.algorithm
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded