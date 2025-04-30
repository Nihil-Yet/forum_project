# установленные модули
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# собственные модули

# routers
from routers.users import routerUsers
from routers.groups import routerGroups
from routers.posts import routerPosts
from routers.comments import routerComments
from routers.tags import routerTags

# Приложение
app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=3600,  # Указывает, как долго браузер может кэшировать CORS-ответы
)

app.include_router(router=routerUsers, prefix="/api", tags=["Users"])
app.include_router(router=routerGroups, prefix="/api", tags=["Groups"])
app.include_router(router=routerPosts, prefix="/api", tags=["Posts"])
app.include_router(router=routerComments, prefix="/api", tags=["Comments"])
app.include_router(router=routerTags, prefix="/api", tags=["Tags"])

if __name__ == "__main__":
    uvicorn.run("mainApp:app", reload = True)