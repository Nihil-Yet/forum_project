# установленные модули
import aiomysql
from fastapi import APIRouter, HTTPException, Depends
import logging

# собственные модули
from settings.database import database_connect
from settings.schemes import CommentSchema

routerComments = APIRouter()

# создание поста
@routerComments.post("/posts/create/")
async def create_comment(new_comment: CommentSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `users` WHERE `id` = %s""", (new_comment.user_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "User not found")
            await cursor.execute("""SELECT * FROM `posts` WHERE `id` = %s""", (new_comment.post_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "Post not found")
            await cursor.execute(
                """INSERT INTO `comments` (user_id, post_id, comment_text) 
                VALUES (%s, %s, %s);""",
                (new_comment.user_id, new_comment.post_id, new_comment.comment_text,))
            await connection.commit()
            new_comment_id = cursor.lastrowid
            return {
                "message": "Comment create successfully",
                "post_id": new_comment_id,
            }
    finally:
        if connection: connection.close()