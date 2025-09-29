from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class PasswordResetRequest(BaseModel):
    email: str


class NewPasswordRequest(BaseModel):
    new_password: str
