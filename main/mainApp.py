# установленные модули
import aiomysql
import uvicorn
from fastapi import FastAPI, HTTPException, Depends

# собственные модули
from settings.database import database_connect
from settings.config import appSettings
from auth import auth_utils
from settings.schemes import AddGroupSchema

# routers
from routers.users import routerUsers

# Приложение
app = FastAPI()

app.include_router(router=routerUsers, prefix="/api", tags=["Users"])

# функция добавления группы
@app.post("/api/groups/create/", tags = ["Groups"])
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

if __name__ == "__main__":
    uvicorn.run("mainApp:app", reload = True)