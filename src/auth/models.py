from pydantic import BaseModel, Field, EmailStr


class UserSchema(BaseModel):
    username: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "username": "Joe",
                "email": "Joe@x.com",
                "password": "the_password",
            }
        }
        orm_mode = True


class UserLoginSchema(BaseModel):
    username: str = Field(...)
    password: str = Field(...)

    class Config:
        schema_extra = {"example": {"username": "Joe", "password": "the_password"}}
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


class LoginCheckResponse(BaseModel):
    success: bool
