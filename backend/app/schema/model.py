from pydantic import BaseModel, Field, EmailStr
from typing import Optional,List


class PostSchema(BaseModel):
    owner: Optional[str] = None
    id: Optional[int] = None
    title: str = Field(...)
    content: str = Field(...)
    shared_users: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "title": "Securing FastAPI applications with JWT.",
                "content": "In this tutorial, you'll learn how to secure your application by enabling authentication using JWT. We'll be using PyJWT to sign, encode and decode JWT tokens...."
            }
        }


class UserSchema(BaseModel):

    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {

                "email": "joe@xyz.com",
                "password": "any"
            }
        }


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "email": "joe@xyz.com",
                "password": "any"
            }
        }


class ShareNoteSchema(BaseModel):
    shared_users: List[str]

    class Config:
        schema_extra = {
            "example": {
                "shared_users": ["user1@example.com", "user2@example.com"]
            }
        }


class ReplyRoverInput(BaseModel):
    host: str
    api_key: str