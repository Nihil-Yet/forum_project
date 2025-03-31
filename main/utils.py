import bcrypt
import jwt

from main.config import AuthJWT

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
        private_key: str = AuthJWT.private_key_path.read_text(), 
        algorithm: str = AuthJWT.algorithm
):
    encoded = jwt.encode(payload, private_key, algorithm=algorithm,)
    return encoded

def decode_JWT(
        token: str | bytes, 
        public_key: str = AuthJWT.public_key_path.read_text(), 
        algorithm: str = AuthJWT.algorithm
):
    decoded = jwt.decode(token, public_key, algorithms=[algorithm])
    return decoded