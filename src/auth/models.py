from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "Abdulazeez Abdulazeez Adeshina",
                "email": "abdulazeez@x.com",
                "password": "weakpassword",
            }
        }
        orm_mode = True


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {"email": "abdulazeez@x.com", "password": "weakpassword"}
        }
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str


class TokenContent(BaseModel):
    user_id: str
    expires: float


class LoginFailureMessage(BaseModel):
    detail: str

    class Config:
        schema_extra = {
            "example": {"detail": "The reason why the authenticaion failed"}
        }
