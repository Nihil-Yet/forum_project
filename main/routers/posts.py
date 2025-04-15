# установленные модули
import aiomysql
from fastapi import APIRouter, HTTPException, Depends
import logging

# собственные модули
from settings.database import database_connect
from settings.schemes import PostSchema

routerPosts = APIRouter()

# создание поста
@routerPosts.post("/posts/create/")
async def create_post(new_post: PostSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users` WHERE `id` = %s""", (new_post.user_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "User not found")
            await cursor.execute("""SELECT * FROM `groups` WHERE `id` = %s""", (new_post.group_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "Group not found")
            await cursor.execute(
                """INSERT INTO `posts` (user_id, group_id, isUrgently, post_name, post_text) 
                VALUES (%s, %s, %s, %s, %s)""",
                (new_post.user_id, new_post.group_id, new_post.isUrgently,
                 new_post.post_name, new_post.post_text,))
            await connection.commit()
            new_post_id = cursor.lastrowid
            return {
                "message": "Post create successfully",
                "post_id": new_post_id,
            }
    finally:
        if connection: connection.close()

# получение информации обовсех постах
@routerPosts.get("/posts/")
async def get_posts():
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `posts`;""")
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "posts not found")
            return query_result
    finally:
        if connection: connection.close()

# получение информации обовсех постах в группе
@routerPosts.get("/posts/{group_id}/")
async def get_group_posts(group_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `posts` WHERE `group_id` = %s;""", (group_id,))
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "posts not found or group not exist")
            return query_result
    finally:
        if connection: connection.close()

# получение информации обовсех постах пользователя
@routerPosts.get("/posts/{user_id}/")
async def get_user_posts(user_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `posts` WHERE `user_id` = %s;""", (user_id,))
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "posts not found or user not exist")
            return query_result
    finally:
        if connection: connection.close()

# информация о посте
@routerPosts.get("/posts/{post_id}/")
async def get_post(post_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `posts` WHERE `id` = %s;""", (post_id,))
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "post not found")
            return query_result
    finally:
        if connection: connection.close()
