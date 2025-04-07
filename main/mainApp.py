# установленные модули
import aiomysql
import uvicorn
from fastapi import FastAPI, HTTPException, Depends

# собственные модули
from settings.database import database_connect
from settings.config import appSettings

# routers
from routers.users import routerUsers
from routers.groups import routerGroups

# Приложение
app = FastAPI()

app.include_router(router=routerUsers, prefix="/api", tags=["Users"])
app.include_router(router=routerGroups, prefix="/api", tags=["Groups"])


if __name__ == "__main__":
    uvicorn.run("mainApp:app", reload = True)