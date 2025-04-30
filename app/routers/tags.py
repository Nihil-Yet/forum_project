# установленные модули
import aiomysql
from fastapi import APIRouter, HTTPException, Depends
import logging

# собственные модули
from settings.database import database_connect
from settings.schemes import PostSchema, AddPostSchema, UserSchema

routerTags = APIRouter()

@routerTags.post("/tags/create/{tag_name}/")
async def create_tag(tag_name: str):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `tags` WHERE `tag_name` = %s""", 
                (tag_name,))
            if cursor.fetchone():
                raise HTTPException(
                    status_code=409, detail="This tag alredy exist")
    finally:
        if connection: connection.close()