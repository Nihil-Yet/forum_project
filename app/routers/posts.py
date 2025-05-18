# установленные модули
from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime

# собственные модули
from settings.database import database_connect
from settings.schemes import PostSchema, AddPostSchema, UserSchema
from auth import get_jwt_payload

routerPosts = APIRouter()

# создание поста
@routerPosts.post("/posts/create/")
async def create_post(
    new_post: AddPostSchema,
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
            if new_post.group_id != 0:
                await cursor.execute(
                    """SELECT * FROM `groups` WHERE `id` = %s""",
                    (new_post.group_id,))
                if not await cursor.fetchone():
                    raise HTTPException(status_code = 404, detail = "Group not found")
                await cursor.execute(
                """SELECT * FROM `user_group` WHERE `user_id` = %s AND `group_id` = %s""",
                (user_token["id"], new_post.group_id))
                if not await cursor.fetchone():
                    raise HTTPException(
                        status_code = 404,
                        detail = f"User {user_token["id"]} not in group {new_post.group_id}")
            if new_post.group_id == 0:
                new_post.group_id = None
            await cursor.execute(
                """INSERT INTO `posts` (user_id, group_id, isUrgently, post_name, post_text, creation_time) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (user_token["id"], new_post.group_id, new_post.isUrgently,
                 new_post.post_name, new_post.post_text, datetime.now()))
            await connection.commit()
            new_post_id = cursor.lastrowid
            return {
                "message": "Post create successfully",
                "post_id": new_post_id,
            }
    finally:
        if connection: connection.close()

# Добавление тега к посту
@routerPosts.post("/posts/{post_id}/tags/{tag_name}/add/")
async def add_post_tag(post_id: int, tag_name: str):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `posts` WHERE `id` = %s;""", 
                (post_id,))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=404, detail="Post not found")
            await cursor.execute(
                """SELECT * FROM `tags` WHERE `tag_name` = %s;""", 
                (tag_name,))
            tag_inf = await cursor.fetchone()
            if not tag_inf:
                raise HTTPException(
                    status_code=404, detail="Tag not found")
            await cursor.execute(
                """INSERT INTO `tag_post` (tag_id, post_id) VALUES (%s, %s);""",
                (tag_inf["id"], post_id)
            )
            await connection.commit()
            return {"message": "tag added successfully"}
    finally:
        if connection: connection.close()

# изменение статуса срочности
@routerPosts.post("/posts/{post_id}/status/{isUrgently}/")
async def change_post_status(
    post_id: int, isUrgently: bool,
    user_token: UserSchema = Depends(get_jwt_payload)
    ):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `posts` WHERE `id` = %s""",
                (post_id,))
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
            if not (post_inf["user_id"] == user_token["id"] or user_role["role_id"] in (1, 2)):
                raise HTTPException(
                    status_code = 403,
                    detail = f"User {user_token["id"]} not have enough rights")
            await cursor.execute(
                """UPDATE `posts` SET `isUrgently` = %s WHERE `id` = %s""",
                (isUrgently, post_id))
            await connection.commit()
            return {"message": "Post status change successfully"}
    finally:
        if connection: connection.close()

# получение информации обо всех постах
@routerPosts.get("/posts/")
async def get_posts():
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT p.*, u.user_name
                FROM `posts` p
                JOIN `users` u ON p.user_id = u.id
                ORDER BY p.isUrgently DESC, p.creation_time ASC;""")
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "Posts not found")
            return query_result
    finally:
        if connection: connection.close()

# получение постов по тегам
@routerPosts.get("/posts/by_tags/")
async def get_posts_by_tags(tag_ids: list[int] = Query(...)):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            tag_placeholders = ','.join(['%s'] * len(tag_ids))
            query = f"""
                SELECT p.*, u.user_name
                FROM posts p
                JOIN users u ON p.user_id = u.id
                WHERE p.id IN (
                    SELECT tp.post_id
                    FROM tag_post tp
                    WHERE tp.tag_id IN ({tag_placeholders})
                    GROUP BY tp.post_id
                    HAVING COUNT(DISTINCT tp.tag_id) = %s
                )
                ORDER BY p.isUrgently DESC, p.creation_time ASC;"""
            await cursor.execute(query, (*tag_ids, len(tag_ids)))
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code=404, detail="Posts not found")
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
            await cursor.execute(
                """SELECT p.*, u.user_name
                FROM `posts` p
                JOIN `users` u ON p.user_id = u.id
                WHERE p.id = %s;""",
                (post_id))
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(status_code = 404, detail = "Post not found")
            return query_result
    finally:
        if connection: connection.close()

# получение тегов поста
@routerPosts.get("/posts/{post_id}/tags/")
async def get_post_tags(post_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `posts` WHERE `id` = %s;""", 
                (post_id,))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code=404, detail="Post not found")
            await cursor.execute(
                """SELECT tp.id, tp.tag_id, tp.post_id, t.tag_name
                FROM tag_post tp
                JOIN `tags` t ON tp.tag_id = t.id
                WHERE tp.post_id = %s""",
                (post_id,)
            )
            post_tags = await cursor.fetchall()
            if not post_tags:
                raise HTTPException(
                    status_code=404, detail="Tags not found")
            return post_tags
    finally:
        if connection: connection.close()

# получения комментариев под постом
@routerPosts.get("/posts/{post_id}/comments/")
async def get_post_comments(post_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `posts` WHERE `id` = %s
                ORDER BY `creation_time` ASC""", (post_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "Post not found")
            await cursor.execute(
                """SELECT c.*, u.user_name
                FROM `comments` c
                JOIN `users` u ON c.user_id = u.id
                WHERE c.post_id = %s
                ORDER BY c.creation_time ASC""",
                (post_id,))
            post_comments = await cursor.fetchall()
            return post_comments
    finally:
        if connection: connection.close()

# удаление поста
@routerPosts.delete("/posts/{post_id}/")
async def delete_post(
    post_id: int,
    user_token: UserSchema = Depends(get_jwt_payload)
    ):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT * FROM `posts` WHERE `id` = %s""", (post_id,))
            post_inf = await cursor.fetchone()
            if not post_inf:
                raise HTTPException(status_code = 404, detail = "Post not found")
            if post_inf["user_id"] != user_token["id"]:
                await cursor.execute(
                    """SELECT `role_id` 
                    FROM `user_group` WHERE `group_id` = %s AND `user_id` = %s""",
                    (post_inf["group_id"], user_token["id"],))
                user_role = await cursor.fetchone()
                if not user_role:
                    raise HTTPException(
                        status_code=403, 
                        detail="User not in the group")
                if not (user_role["role_id"] in (1, 2)):
                    raise HTTPException(
                        status_code = 403,
                        detail = f"User {user_token["id"]} not have enough rights")
            await cursor.execute("""DELETE FROM `posts` WHERE `id` = %s""", (post_id,))
            await connection.commit()
            return {"message": "post delete successful"}
    finally:
        if connection: connection.close()