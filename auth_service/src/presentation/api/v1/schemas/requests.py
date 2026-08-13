from pydantic import BaseModel, Field


class SendVerificationRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)


class SignupRequest(BaseModel):
    verify_token: str = Field(..., min_length=36, max_length=36)
    password: str = Field(..., min_length=8, max_length=128)
    device: str = Field(default="unknown", min_length=1, max_length=50)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=1, max_length=128)
    device: str = Field(default="unknown", min_length=1, max_length=50)


class LogoutRequest(BaseModel):
    device: str = Field(default="unknown", min_length=1, max_length=50)


class DeleteAccountRequest(BaseModel):
    device: str = Field(default="unknown", min_length=1, max_length=50)


class ForgetPasswordRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)


class ResetPasswordRequest(BaseModel):
    verify_token: str = Field(..., min_length=36, max_length=36)
    new_password: str = Field(..., min_length=8, max_length=128)


class SetPasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=8, max_length=128)
    device: str = Field(default="unknown", min_length=1, max_length=50)


class RevokeSessionRequest(BaseModel):
    session_id: str = Field(..., min_length=36, max_length=36)
    device: str = Field(default="unknown", min_length=1, max_length=50)


class RevokeAllOtherRequest(BaseModel):
    device: str = Field(default="unknown", min_length=1, max_length=50)


class RotateTokensRequest(BaseModel):
    refresh_token: str = Field(..., min_length=10)
    device: str = Field(default="unknown", min_length=1, max_length=50)
