# установленные модули
import aiomysql
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

# собственные модули
from settings.config import appSettings
from auth import auth_utils
from settings.schemes import UserSchema, AddUserSchema, LoginUserSchema, AddGroupSchema

# функция подключения к базе данных
async def database_connect():
    try:
        return await aiomysql.connect(
            host=appSettings.dbSettings.host,
            port=appSettings.dbSettings.port,
            user=appSettings.dbSettings.user,
            password=appSettings.dbSettings.password,
            db=appSettings.dbSettings.name,
            cursorclass=aiomysql.cursors.DictCursor
        )
    except aiomysql.MySQLError as ex:
        raise HTTPException(status_code=500, detail=f"Database error: {ex}")

app = FastAPI()

# функция добавления юзера в БД
@app.post("/api/users/create/", tags=["Users"])
async def add_user(new_user: AddUserSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id` FROM `users` WHERE `login` = %s""", (new_user.login,))
            user_login = await cursor.fetchone()
            if user_login:
                raise HTTPException(status_code=400, detail="Login already exists")
            hash_pass = auth_utils.hash_password(new_user.password)
            await cursor.execute("""INSERT INTO `users` (user_name, login, password) VALUES (%s, %s, %s)""",
                                  (new_user.user_name.strip().title(), new_user.login, hash_pass))
            await connection.commit()
            return {"message": "User added successfully"}
    finally:
        if connection: connection.close()

# функция аутентификации/авторизации юзера
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
            if not auth_utils.check_password(user['password'], authorized_user.password):
                raise HTTPException(status_code=401, detail="Invalid login or password")
            jwt_payload = {
                "sub": "user",
                "id": user["id"],
                "login": authorized_user.login,
                "username": user["user_name"]
                }
            token = auth_utils.encode_JWT(jwt_payload)
            return {
                "message": "Login successful", 
                "access_JWT": token,
                "token_type": "Byarer",
                }
    finally:
        if connection: connection.close()


# функция проверки аутентификации/авторизации юзера
@app.get("/api/users/login_check/", tags=["Users"])
async def check_auth_user(
    user_token: UserSchema = Depends(auth_utils.get_jwt_payload)
):
    return {
        "sub": user_token["sub"],
        "id": user_token["id"],
        "login": user_token["login"],
        "username": user_token["username"],
    }
    

# функция получения информации о всех зарегестрированных пользователях
@app.get("/api/users/", tags = ["Users"])
async def get_users():
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id`, `user_name`, `login` FROM `users`;""")
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "users are not found")
            return query_result
    finally:
        if connection: connection.close()

# функция получения информации о пользователе по его id
@app.get("/api/users/{user_id}/", tags = ["Users"])
async def get_user(user_id: int) -> UserSchema:
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users` WHERE id = %s;""", (user_id,))
            query_result = await cursor.fetchone()
            if not query_result:
                raise HTTPException(status_code = 404, detail = f"user with id = {user_id} not found")
            return UserSchema(**query_result)
    finally:
        if connection: connection.close()

# функция удаления пользователя по его id
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


# функция добавления группы
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
    uvicorn.run("mainApp:app", reload = True)