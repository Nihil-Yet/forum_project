# установленные модули
from pydantic import BaseModel, Field

# схема юзера для его добавления в БД
class UserSchema(BaseModel):
    user_name: str = Field(min_length=1, max_length=255)
    login: str = Field(min_length=1, max_length=255)
    is_studen: bool = False

class AddUserSchema(UserSchema):
    password: str = Field(min_length=8, max_length=100)

# схема юзера для аутентификации/авторизации
class LoginUserSchema(BaseModel):
    login: str = Field(min_length=1, max_length=255)
    password: str = Field(max_length=100)


# схема для добавления группы
class GroupSchema(BaseModel):
    group_name: str = Field(min_length = 1, max_length = 255)
    description: str = Field(max_length=1024)

# схема пользователя в группе
class GroupMember(BaseModel):
    user_id: int
    group_id: int

class JoinGroupMember(GroupMember):
    role_id: int = 3

class PostSchema(BaseModel):
    group_id: int
    isUrgently: bool = 1 # Срочно/Не срочно
    post_name: str = Field(min_length = 1, max_length = 255)
    post_text: str = Field(min_length = 1)

class CommentSchema(BaseModel):
    post_id: int
    comment_text: str