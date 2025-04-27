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
async def create_post(
    new_post: PostSchema,
    ):
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

# изменение статуса срочности
@routerPosts.post("/posts/status/")
async def change_post_status(post_id: int, isUrgently: bool):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `posts` WHERE `id` = %s""", (post_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "Post not found")
            await cursor.execute(
                """UPDATE `posts` SET `isUrgently` = %s WHERE `id` = %s""",
                (isUrgently, post_id))
            await connection.commit()
            return {"message": "Post status change successfully"}
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
                raise HTTPException(status_code = 404, detail = "Posts not found")
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
                raise HTTPException(status_code = 404, detail = "Post not found")
            return query_result
    finally:
        if connection: connection.close()

# получения комментариев под постом
@routerPosts.post("/posts/{post_id}/comments")
async def get_post_comments(post_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `posts` WHERE `id` = %s""", (post_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "Post not found")
            await cursor.execute("""SELECT * FROM `comments` WHERE `post_id` = %s""",
                                 (post_id,))
            post_comments = await cursor.fetchall()
            return post_comments
    finally:
        if connection: connection.close()

# удаление поста
@routerPosts.delete("/posts/{post_id}/")
async def delete_post(post_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `posts` WHERE `id` = %s""", (post_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "Post not found")
            await cursor.execute("""DELETE FROM `posts` WHERE `id` = %s""", (post_id,))
            await connection.commit()
            return {"message": "post delete successful"}
    finally:
        if connection: connection.close()