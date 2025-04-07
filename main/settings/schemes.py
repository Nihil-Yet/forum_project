# установленные модули
from pydantic import BaseModel, Field

# схема юзера для его добавления в БД
class UserSchema(BaseModel):
    user_name: str = Field(min_length=1, max_length=255)
    login: str = Field(min_length=1, max_length=255)

class AddUserSchema(UserSchema):
    password: str = Field(min_length=8, max_length=100)

# схема юзера для аутентификации/авторизации
class LoginUserSchema(BaseModel):
    login: str = Field(min_length=1, max_length=255)
    password: str = Field(max_length=100)


# схема для добавления группы
class AddGroupSchema(BaseModel):
    group_name: str = Field(min_length = 1, max_length = 255)