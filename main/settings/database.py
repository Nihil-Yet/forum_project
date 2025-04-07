# установленные модули
import aiomysql
from fastapi import HTTPException

# собственные модули
from settings.config import appSettings

# функция подключения к базе данных
async def database_connect():
    try:
        return await aiomysql.connect(
            host=appSettings.dbSettings.host,
            port=appSettings.dbSettings.port,
            user=appSettings.dbSettings.user,
            password=appSettings.dbSettings.password,
            db=appSettings.dbSettings.name,
            cursorclass=aiomysql.cursors.DictCursor
        )
    except aiomysql.MySQLError as ex:
        raise HTTPException(status_code=500, detail=f"Database error: {ex}")