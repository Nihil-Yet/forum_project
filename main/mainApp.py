# установленные модули
import uvicorn
from fastapi import FastAPI

# собственные модули

# routers
from routers.users import routerUsers
from routers.groups import routerGroups

# Приложение
app = FastAPI()

app.include_router(router=routerUsers, prefix="/api", tags=["Users"])
app.include_router(router=routerGroups, prefix="/api", tags=["Groups"])

if __name__ == "__main__":
    uvicorn.run("mainApp:app", reload = True)