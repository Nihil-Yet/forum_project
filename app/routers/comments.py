# установленные модули
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging

# собственные модули
from settings.database import database_connect
from settings.schemes import CommentSchema, UserSchema
from auth import get_jwt_payload

routerComments = APIRouter()

# создание комментария
@routerComments.post("/comments/create/")
async def create_comment(
    new_comment: CommentSchema,
    user_token: UserSchema = Depends(get_jwt_payload)
    ):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `users` WHERE `id` = %s""",
                (user_token["id"],))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "User not found")
            await cursor.execute(
                """SELECT * FROM `posts` WHERE `id` = %s""", (new_comment.post_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "Post not found")
            await cursor.execute(
                """INSERT INTO `comments` (user_id, post_id, comment_text, creation_time) 
                VALUES (%s, %s, %s, %s);""",
                (user_token["id"], new_comment.post_id, new_comment.comment_text, datetime.now()))
            await connection.commit()
            new_comment_id = cursor.lastrowid
            await cursor.execute(
                """UPDATE `posts` SET `comments_num` = `comments_num` + 1, `isUrgently` = 0 WHERE `id`=%s""",
                (new_comment.post_id,)
            )
            await connection.commit()
            return {
                "message": "Comment create successfully",
                "comment_id": new_comment_id,
            }
    finally:
        if connection: connection.close()

# получения комментария по id
@routerComments.get("/comments/{comment_id}/")
async def get_comment(comment_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `comments` WHERE `id` = %s""", (comment_id,))
            comment_inf = await cursor.fetchone()
            if not comment_inf:
                raise HTTPException(status_code = 404, detail = "Comment not found")
            return comment_inf
    finally:
        if connection: connection.close()

# удаление комментария
@routerComments.delete("/comments/{comment_id}/")
async def delete_comment(
    comment_id: int,
    user_token: UserSchema = Depends(get_jwt_payload)
    ):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `comments` WHERE `id` = %s""", (comment_id,))
            comment_inf = await cursor.fetchone()
            if not comment_inf:
                raise HTTPException(status_code = 404, detail = "Comment not found")
            if comment_inf["user_id"] != user_token["id"]:
                await cursor.execute(
                    """SELECT `group_id` FROM `posts` WHERE `id` = %s""",
                    (comment_inf["post_id"],))
                post_inf = await cursor.fetchone()
                if not post_inf:
                    raise HTTPException(status_code = 404, detail = "Post not found")
                await cursor.execute(
                    """SELECT `role_id` 
                    FROM `user_group` WHERE `group_id` = %s AND `user_id` = %s""",
                    (post_inf["group_id"], user_token["id"],))
                user_role = await cursor.fetchone()
                if not user_role:
                    raise HTTPException(status_code=403, detail="User not in the group")
                if not (user_role["role_id"] in (1, 2)):
                    raise HTTPException(
                        status_code = 403,
                        detail = f"User {user_token["id"]} not have enough rights")

            await cursor.execute("""DELETE FROM `comments` WHERE `id` = %s""", (comment_id,))
            await cursor.execute(
                """UPDATE `posts` SET `comments_num` = `comments_num` - 1 WHERE `id`=%s""",
                (comment_inf["post_id"],)
            )
            await connection.commit()
            return {"message": "comment delete successful"}
    finally:
        if connection: connection.close()