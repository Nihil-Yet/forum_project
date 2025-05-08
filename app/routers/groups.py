# установленные модули
import aiomysql
from fastapi import APIRouter, HTTPException, Depends
import logging

# собственные модули
from settings.database import database_connect
from settings.schemes import GroupSchema, \
    LeftGroupMember, JoinGroupMember, UserSchema
from auth import get_jwt_payload

routerGroups = APIRouter()

# функция добавления группы
@routerGroups.post("/groups/create/")
async def add_group(
    new_group: GroupSchema,
    user_token: UserSchema = Depends(get_jwt_payload)
    ):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id` FROM `groups` WHERE `group_name` = %s""",
                                 (new_group.group_name))
            group_exist = await cursor.fetchone()
            if group_exist:
                raise HTTPException(status_code=409, detail="This group name already used")
            await cursor.execute("""INSERT INTO `groups` (group_name, description) VALUES (%s, %s);""", 
                                 (new_group.group_name, new_group.description))
            await connection.commit()
            new_group_id = cursor.lastrowid
            await cursor.execute("""INSERT INTO `user_group` (user_id, group_id, role_id) VALUES (%s, %s, %s);""",
                                 (user_token["id"], new_group_id, 1,))
            await connection.commit()
            return {
                "message": "Group added succesfully",
                "group_id": new_group_id,
                }
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection: connection.close()

# функция получения информации о всех существующих группах
@routerGroups.get("/groups/")
async def get_groups():
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id`, `group_name`, `description` FROM `groups`""")
            groups = await cursor.fetchall()
            if not groups:
                raise HTTPException(status_code = 404, detail = "groups are not found")
            return groups
    finally:
        if connection:
            connection.close()

# функция получения информации о группе по id
@routerGroups.get("/groups/{group_id}/")
async def get_group(group_id: int) -> GroupSchema:
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `groups` WHERE id = %s;""", (group_id,))
            query_result = await cursor.fetchone()
            if not query_result:
                raise HTTPException(status_code = 404, detail = f"group with id = {group_id} not found")
            return GroupSchema(**query_result)
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection:
            connection.close()

# функция вступления в группу
@routerGroups.post("/groups/members/join/")
async def joining_member(
    new_member: JoinGroupMember,
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
                raise HTTPException(
                    status_code=404,
                    detail=f"User with id = {user_token["id"]} not found")
            await cursor.execute(
                """SELECT * FROM `groups` WHERE `id` = %s""",
                (new_member.group_id,))
            if not await cursor.fetchone():
                raise HTTPException(status_code=404, detail=f"Group with id = {new_member.group_id} not found")
            await cursor.execute(
                """SELECT `id` FROM `user_group` WHERE `user_id` = %s AND `group_id` = %s;""",
                (user_token["id"], new_member.group_id,))
            if await cursor.fetchone():
                raise HTTPException(
                    status_code=409,
                    detail="This user is already a member of this group")
            await cursor.execute(
                """INSERT INTO `user_group` (user_id, group_id, role_id) VALUES (%s, %s, %s);""",
                (user_token["id"], new_member.group_id, new_member.role_id,))
            await connection.commit()
            return {"message": "User has successfully joined the group"}
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection: 
            connection.close()

# функция выхода из группы
@routerGroups.post("/groups/members/left/")
async def left_member(
    left_member: LeftGroupMember,
    user_token: UserSchema = Depends(get_jwt_payload)
    ):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT `id` FROM `user_group` WHERE `user_id` = %s AND `group_id` = %s;""",
                (user_token["user_id"], left_member.group_id,))
            isUser = await cursor.fetchone()
            if not isUser:
                raise HTTPException(
                    status_code=404,
                    detail=f"User with id = {user_token["user_id"]} not found in group with id = {left_member.group_id} or this group not exist")
            await cursor.execute(
                """DELETE FROM `user_group` WHERE `id` = %s""",
                (isUser["id"],))
            await connection.commit()
            return {"message": "User has successfully left the group"}
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection:
            connection.close()

# функция получения информации о всех членах группы по её id
@routerGroups.get("/groups/{group_id}/members/")
async def get_group_members(group_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT `id` FROM `groups` WHERE `id` = %s""",
                (group_id))
            if not await cursor.fetchone():
                raise HTTPException(status_code = 404, detail = "Group not found")
            await cursor.execute(
                """SELECT `id`, `user_id`, `role_id` FROM user_group WHERE `group_id` = %s""",
                (group_id,))
            group_members = await cursor.fetchall()
            if not group_members:
                raise HTTPException(
                    status_code = 404,
                    detail = f"No members in the group with id = {group_id}")
            return group_members
    finally:
        if connection:
            connection.close()

# получение информации обовсех постах в группе
@routerGroups.get("/groups/{group_id}/posts")
async def get_group_posts(group_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute(
                """SELECT p.*, u.user_name
                FROM `posts` p
                JOIN `users` u ON p.user_id = u.id
                WHERE `group_id` = %s
                ORDER BY p.isUrgently DESC, p.creation_time ASC;""",
                (group_id,))
            query_result = await cursor.fetchall()
            if not query_result:
                raise HTTPException(
                    status_code = 404,
                    detail = "Posts not found or group not exist")
            return query_result
    finally:
        if connection: connection.close()

# функция удаления группы по id
@routerGroups.delete("/groups/{group_id}/")
async def delete_group(
    group_id: int,
    user_token: UserSchema = Depends(get_jwt_payload)
    ):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `groups` WHERE id = %s;""", (group_id,))
            if not await cursor.fetchone():
                raise HTTPException(
                    status_code = 404,
                    detail = f"group with id = {group_id} not found")
            await cursor.execute(
                """SELECT * FROM `user_group` WHERE `user_id` = %s AND `group_id` = %s;""",
                (user_token["id"], group_id,))
            user = await cursor.fetchone()
            if not user:
                raise HTTPException(
                    status_code = 404,
                    detail = f"user {user_token["id"]} not in group {group_id}")
            if user["role_id"] != 1:
                raise HTTPException(
                    status_code = 403,
                    detail = f"user {user_token["id"]} not have enough rights")
            await cursor.execute("""DELETE FROM `groups` WHERE `id` = %s;""", (group_id,))
            await connection.commit()
            return {"message": "Group delete succesfully"}
    except aiomysql.MySQLError as ex:
        logging.error(f"{ex}")
    finally:
        if connection: connection.close()