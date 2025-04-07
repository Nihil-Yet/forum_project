# установленные модули
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

# собственные модули
from settings.database import database_connect
from settings.config import appSettings
from auth import auth_utils
from settings.schemes import AddGroupSchema

routerGroups = APIRouter()

# функция добавления группы
@routerGroups.post("/groups/create/", tags = ["Groups"])
async def add_group(new_group: AddGroupSchema):
    connection = None
    try:
        connection = await database_connect()
        async with connection.cursor() as cursor:
            await cursor.execute("""INSERT INTO `groups` (group_name) VALUES (%s)""", 
                                 (new_group.group_name,))
            await connection.commit()
            return {"message": "User added succesfully"}
    finally:
        if connection: connection.close()