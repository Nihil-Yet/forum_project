import uvicorn
from fastapi import FastAPI, APIRouter

# Роутер для пользователей
user_router = APIRouter()

@user_router.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

# Роутер для товаров
item_router = APIRouter()

@item_router.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id}

# Основное приложение
app = FastAPI()

# Включаем роутеры в основное приложение
app.include_router(user_router, prefix="/users")
app.include_router(item_router, prefix="/items")

if __name__ == "__main__":
    uvicorn.run("test:app", reload = True)