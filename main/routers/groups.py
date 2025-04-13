# установленные модули
from fastapi import APIRouter, HTTPException, Depends
import logging

# собственные модули
from settings.database import database_connect
from settings.schemes import GroupSchema

routerGroups = APIRouter()

# функция добавления группы
@routerGroups.post("/groups/create/")
async def add_group(new_group: GroupSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id` FROM `groups` WHERE `group_name` = %s""",
                                 (new_group.group_name))
            group_exist = await cursor.fetchone()
            if group_exist:
                raise HTTPException(status_code=409, detail="This group name already used")
            await cursor.execute("""INSERT INTO `groups` (group_name, description) VALUES (%s, %s)""", 
                                 (new_group.group_name, new_group.description))
            await connection.commit()
            return {"message": "Group added succesfully"}
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
        if connection: connection.close()

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
    finally:
        if connection: connection.close()

# функция удаления группы по id
@routerGroups.delete("/groups/{group_id}/")
async def delete_group(group_id: int):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT * FROM `groups` WHERE id = %s;""", (group_id,))
            query_result = await cursor.fetchone()
            if not query_result:
                raise HTTPException(status_code = 404, detail = f"group with id = {group_id} not found")
            await cursor.execute("""DELETE FROM `groups` WHERE `id` = %s;""", (group_id,))
            await connection.commit()
            return {"message": "Group delete succesfully"}
    finally:
        if connection: connection.close()