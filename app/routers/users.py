# установленные модули
import aiomysql
from fastapi import APIRouter, HTTPException, Depends
import logging

# собственные модули
from settings.database import database_connect
from auth import auth_utils
from settings.schemes import UserSchema, AddUserSchema, LoginUserSchema

routerUsers = APIRouter()

# функция добавления юзера в БД
@routerUsers.post("/users/create/")
async def add_user(new_user: AddUserSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id` FROM `users` WHERE `login` = %s""", (new_user.login,))
            login_exist = await cursor.fetchone()
            if login_exist:
                raise HTTPException(status_code=409, detail="Login already exists")
            hash_pass = auth_utils.hash_password(new_user.password)
            await cursor.execute("""INSERT INTO `users` (user_name, login, password, is_student) VALUES (%s, %s, %s, %s)""",
                                  (new_user.user_name.strip().title(), new_user.login, hash_pass, new_user.is_studen))
            await connection.commit()
            new_user_id = cursor.lastrowid
            jwt_payload = {
                "sub": "user",
                "id": new_user_id,
                "login": new_user.login,
                "username": new_user.user_name.strip().title(),
                "is_student": new_user.is_studen,
                }
            token = auth_utils.encode_JWT(jwt_payload)
            return {
                "message": "User added successfully",
                "user_id": new_user_id,
                "access_JWT": token,
            }
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection: connection.close()

# функция аутентификации/авторизации юзера
@routerUsers.post("/users/login/")
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
                "username": user["user_name"],
                "is_student": user["is_student"],
                }
            token = auth_utils.encode_JWT(jwt_payload)
            return {
                "message": "Login successful", 
                "access_JWT": token,
                "token_type": "Byarer",
                }
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection: connection.close()

# функция проверки аутентификации/авторизации юзера
@routerUsers.get("/users/login_check/")
async def check_auth_user(
    user_token: UserSchema = Depends(auth_utils.get_jwt_payload)
):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `user_name` FROM `users` WHERE `id` = %s;""", (user_token["id"],))
            user_name = await cursor.fetchone()
        return {
            "sub": user_token["sub"],
            "id": user_token["id"],
            "login": user_token["login"],
            "username": user_name["user_name"],
            "is_student": user_token["is_student"],
        }
    finally:
        if connection: connection.close()
    

# функция получения информации о всех зарегестрированных пользователях
@routerUsers.get("/users/")
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
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection: connection.close()

# функция получения информации о пользователе по его id
@routerUsers.get("/users/{user_id}/")
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
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection: connection.close()

# функция редактирования имени юзера
@routerUsers.post("/users/changename/{new_name}/")
async def change_username(
    new_name: str, 
    user_token = Depends(auth_utils.get_jwt_payload)
    ):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users` WHERE `id` = %s;""", (user_token["id"],))
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail="User not found")
            await cursor.execute("""UPDATE `users` SET `user_name` = %s WHERE `id` = %s;""", 
                                 (new_name, user_token["id"],))
            await connection.commit()
            return {
                "message": "username change successful"
            }
    finally:
        if connection: connection.close()

# функция получения информации о всех группах, в которых состоит пользователль
@routerUsers.get("/users/{user_id}/groups/")
async def get_user_groups(user_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id` FROM `users` WHERE `id` = %s""", (user_id))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "User not found")
            await cursor.execute("""
                SELECT ug.id, ug.group_id, ug.role_id, g.group_name
                FROM user_group ug
                JOIN `groups` g ON ug.group_id = g.id
                WHERE ug.user_id = %s
                """, (user_id,))
            user_groups = await cursor.fetchall()
            if not user_groups:
                raise HTTPException(status_code = 404, detail = f"Usegir with id = {user_id} not in any group")
            return user_groups
    finally:
        if connection:
            connection.close()

# получение информации обовсех постах пользователя
@routerUsers.get("/{user_id}/posts/")
async def get_user_posts(user_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""
            SELECT * FROM `posts` WHERE `user_id` = %s;""", (user_id,))
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "Posts not found or user not exist")
            return query_result
    finally:
        if connection: connection.close()

# функция удаления пользователя по его id
@routerUsers.delete("/users/{user_id}/")
async def delete_user(user_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users` WHERE `id` = %s;""", (user_id,))
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(status_code = 404, detail = f"user with id = {user_id} not found")
            await cursor.execute("""DELETE FROM `user_group` WHERE `user_id` = %s""", (user_id,))
            await cursor.execute("""DELETE FROM `users` WHERE `id` = %s;""", (user_id,))
            await connection.commit()
            return {"message": "User delete succesfully"}
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection: connection.close()