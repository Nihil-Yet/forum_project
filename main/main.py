import aiomysql
import uvicorn
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel, Field
import bcrypt
import jwt

from config import host, db_user, db_password, db_name
from futils import hash_password, check_password, \
    encode_JWT, decode_JWT, auth_jwt


# Асинхронная функция подключения к базе данных
async def database_connect():
    try:
        return await aiomysql.connect(
            host=host,
            port=3306,
            user=db_user,
            password=db_password,
            db=db_name,
            cursorclass=aiomysql.cursors.DictCursor
        )
    except aiomysql.MySQLError as ex:
        raise HTTPException(status_code=500, detail=f"Database error: {ex}")

app = FastAPI()

router = APIRouter(prefix="/jwt", tags=["JWT"])

class UserSchema(BaseModel):
    user_name: str = Field(min_length=1, max_length=255)
    login: str = Field(min_length=1, max_length=255)
    user_password: str = Field(min_length=8, max_length=100)

class LoginUserSchema(BaseModel):
    login: str = Field(min_length=1, max_length=255)
    user_password: str = Field(min_length=8, max_length=100)

@app.post("/api/users/create/", tags=["Users"])
async def add_user(new_user: UserSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id` FROM `users` WHERE `login` = %s""", (new_user.login,))
            user_login = await cursor.fetchone()
            if user_login:
                raise HTTPException(status_code=400, detail="Login already exists")
            hash_pass = hash_password(new_user.user_password)
            await cursor.execute("""INSERT INTO `users` (user_name, login, password) VALUES (%s, %s, %s)""",
                                  (new_user.user_name.strip().title(), new_user.login, hash_pass))
            await connection.commit()
            return {"message": "User added successfully"}
    finally:
        if connection: connection.close()

@app.post("/api/users/login/", tags=["Users"])
async def auth_user(authorized_user: LoginUserSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users` WHERE `login` = %s;""", (authorized_user.login,))
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(status_code=401, detail="Invalid login or password")
            if not check_password(user['password'], authorized_user.user_password):
                raise HTTPException(status_code=401, detail="Invalid login or password")
            jwt_payload = {
                "sub": f"user_id: {user["id"]}",
                "login": authorized_user.login,
                "username": user["user_name"]
                }
            token = encode_JWT(jwt_payload)
            return {
                "message": "Login successful", 
                "access_JWT": token,
                "token_type": "Byarer"
                }
    finally:
        if connection: connection.close()

@app.get("/api/users/", tags = ["Users"])
async def get_users():
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users`;""")
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "users are not found")
            return query_result
    finally:
        if connection: connection.close()

@app.get("/api/users/{user_id}/", tags = ["Users"])
async def get_user(user_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users` WHERE id = %s;""", (user_id,))
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = f"user with id = {user_id} not found")
            return query_result
    finally:
        if connection: connection.close()

@app.delete("/api/users/{user_id}/", tags = ["Users"])
async def delete_user(user_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users` WHERE `id` = %s;""", (user_id,))
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(status_code = 404, detail = f"user with id = {user_id} not found")
            await cursor.execute("""DELETE FROM `users` WHERE `id` = %s;""", (user_id,))
            await connection.commit()
            return {"message": "User delete succesfully"}
    finally:
        if connection: connection.close()

class AddGroupSchema(BaseModel):
    group_name: str = Field(min_length = 1, max_length = 255)

@app.post("/api/groups/create/", tags = ["Groups"])
async def add_group(new_group: AddGroupSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""INSERT INTO `groups` (group_name) VALUES (%s)""", 
                                 (new_group.group_name,))
            await connection.commit()
            return {"message": "User added succesfully"}
    finally:
        if connection: connection.close()

if __name__ == "__main__":
    uvicorn.run("main:app", reload = True)