# установленные модули
from fastapi import APIRouter, HTTPException, Depends
import logging

# собственные модули
from settings.database import database_connect
from settings.schemes import GroupSchema

routerGroups = APIRouter()

# функция добавления группы
@routerGroups.post("/groups/create/", tags = ["Groups"])
async def add_group(new_group: GroupSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""SELECT `id` FROM `groups` WHERE `group_name` = %s""",
                                 (new_group.name))
            group_exist = await cursor.fetchone()
            if group_exist:
                raise HTTPException(status_code=409, detail="This group name already used")
            await cursor.execute("""INSERT INTO `groups` (group_name, description) VALUES (%s, %s)""", 
                                 (new_group.name, new_group.description))
            await connection.commit()
            return {"message": "Group added succesfully"}
    finally:
        if connection: connection.close()

# функция получения информации о всех существующих группах
@routerGroups.get("/groups/", tags = ["Groups"])
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