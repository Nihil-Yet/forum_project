# установленные модули
import aiomysql
from fastapi import APIRouter, HTTPException, Depends
import logging

# собственные модули
from settings.database import database_connect
from settings.schemes import PostSchema, AddPostSchema, UserSchema

routerTags = APIRouter()

# Создание тега
@routerTags.post("/tags/create/{tag_name}/")
async def create_tag(tag_name: str):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `tags` WHERE `tag_name` = %s;""", 
                (tag_name,))
            if await cursor.fetchone():
                raise HTTPException(
                    status_code=409, detail="This tag alredy exist")
            await cursor.execute(
                """INSERT INTO `tags` (tag_name) VALUES (%s);""",
                (tag_name)
            )
            await connection.commit()
            return {"message": "tag created success"}
    finally:
        if connection: connection.close()

# Получение списка всех тегов
@routerTags.get("/tags/")
async def get_tags():
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `tags`;""")
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "tags are not found")
            return query_result
    finally:
        if connection: connection.close()