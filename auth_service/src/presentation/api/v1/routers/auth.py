"""Auth HTTP endpoints."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Response, status

from src.application.admin_login import AdminLoginCommand, AdminLoginHandler
from src.application.delete_account import DeleteAccountCommand, DeleteAccountHandler
from src.application.forget_password import ForgetPasswordCommand, ForgetPasswordHandler
from src.application.login import LoginCommand, LoginHandler
from src.application.logout import LogoutCommand, LogoutHandler
from src.application.reset_password import ResetPasswordCommand, ResetPasswordHandler
from src.application.revoke_all_other_sessions import (
    RevokeAllOtherSessionsCommand,
    RevokeAllOtherSessionsHandler,
)
from src.application.revoke_session import RevokeSessionCommand, RevokeSessionHandler
from src.application.rotate_tokens import RotateTokensCommand, RotateTokensHandler
from src.application.send_verification import (
    SendVerificationCommand,
    SendVerificationHandler,
)
from src.application.set_password import SetPasswordCommand, SetPasswordHandler
from src.application.signup import SignupCommand, SignupHandler
from src.exceptions import (
    DatabaseConnectionError,
    DatabaseOperationError,
    DatabaseTimeoutError,
    DeviceMismatchError,
    EmailBlockedError,
    InvalidEmailError,
    InvalidEmailOrPasswordError,
    InvalidPasswordError,
    InvalidVerificationTokenError,
    PermissionDeniedError,
    SessionNotFoundError,
    TokenInfrastructureError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.presentation.api.v1.schemas.requests import (
    AdminLoginRequest,
    DeleteAccountRequest,
    ForgetPasswordRequest,
    LoginRequest,
    LogoutRequest,
    ResetPasswordRequest,
    RevokeAllOtherRequest,
    RevokeSessionRequest,
    RotateTokensRequest,
    SendVerificationRequest,
    SetPasswordRequest,
    SignupRequest,
)
from src.presentation.api.v1.schemas.responses import (
    AccessTokenResponse,
    MessageResponse,
    TokenPairResponse,
)
from src.presentation.dependencies import (
    EmailBlocklistDep,
    EventPublisherDep,
    PasswordHasherDep,
    SessionRepoDep,
    TokenDecoderDep,
    TokenEncoderDep,
    TokenRepoDep,
    UoWFactory,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def _bearer(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    return authorization.removeprefix("Bearer ").strip()


@router.post(
    "/verification",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Send email verification link",
)
async def send_verification(
    body: SendVerificationRequest,
    token_repo: TokenRepoDep,
    events: EventPublisherDep,
    blocklist: EmailBlocklistDep,
) -> Response:
    handler = SendVerificationHandler(token_repo, events, blocklist)
    try:
        await handler.handle(SendVerificationCommand(email=body.email))
    except EmailBlockedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except InvalidEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/signup",
    response_model=TokenPairResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Complete signup with verification token",
)
async def signup(
    body: SignupRequest,
    uow_factory: UoWFactory,
    sessions: SessionRepoDep,
    encoder: TokenEncoderDep,
    hasher: PasswordHasherDep,
    token_repo: TokenRepoDep,
    events: EventPublisherDep,
) -> TokenPairResponse:
    handler = SignupHandler(
        uow_factory(), sessions, encoder, hasher, token_repo, events
    )
    try:
        result = await handler.handle(
            SignupCommand(
                verify_token=body.verify_token,
                password=body.password,
                device=body.device,
            )
        )
    except InvalidVerificationTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except InvalidPasswordError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        )
    except (DatabaseConnectionError, DatabaseTimeoutError) as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)
        )
    except DatabaseOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)
        )
    return TokenPairResponse(
        access_token=result.access_token, refresh_token=result.refresh_token
    )


@router.post(
    "/login",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
)
async def login(
    body: LoginRequest,
    uow_factory: UoWFactory,
    sessions: SessionRepoDep,
    encoder: TokenEncoderDep,
    hasher: PasswordHasherDep,
    events: EventPublisherDep,
) -> TokenPairResponse:
    handler = LoginHandler(uow_factory(), sessions, encoder, hasher, events)
    try:
        result = await handler.handle(
            LoginCommand(email=body.email, password=body.password, device=body.device)
        )
    except InvalidEmailOrPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    except InvalidEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        )
    return TokenPairResponse(
        access_token=result.access_token, refresh_token=result.refresh_token
    )


@router.post(
    "/admin/login",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    summary="Admin login (account + admin secret)",
)
async def admin_login(
    body: AdminLoginRequest,
    uow_factory: UoWFactory,
    sessions: SessionRepoDep,
    encoder: TokenEncoderDep,
    hasher: PasswordHasherDep,
    events: EventPublisherDep,
) -> TokenPairResponse:
    handler = AdminLoginHandler(uow_factory(), sessions, encoder, hasher, events)
    try:
        result = await handler.handle(
            AdminLoginCommand(
                email=body.email,
                password=body.password,
                admin_password=body.admin_password,
                device=body.device,
            )
        )
    except InvalidEmailOrPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenPairResponse(
        access_token=result.access_token, refresh_token=result.refresh_token
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout current session",
)
async def logout(
    body: LogoutRequest,
    sessions: SessionRepoDep,
    decoder: TokenDecoderDep,
    encoder: TokenEncoderDep,
    events: EventPublisherDep,
    authorization: Annotated[str | None, Header()] = None,
) -> Response:
    token = _bearer(authorization)
    handler = LogoutHandler(sessions, decoder, encoder, events)
    try:
        await handler.handle(LogoutCommand(access_token=token, device=body.device))
    except DeviceMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except TokenInfrastructureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/account",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete authenticated account",
)
async def delete_account(
    body: DeleteAccountRequest,
    uow_factory: UoWFactory,
    sessions: SessionRepoDep,
    decoder: TokenDecoderDep,
    encoder: TokenEncoderDep,
    events: EventPublisherDep,
    authorization: Annotated[str | None, Header()] = None,
) -> Response:
    token = _bearer(authorization)
    handler = DeleteAccountHandler(uow_factory(), sessions, decoder, encoder, events)
    try:
        await handler.handle(
            DeleteAccountCommand(access_token=token, device=body.device)
        )
    except DeviceMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except TokenInfrastructureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/password/forgot",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Request password-reset email",
)
async def forget_password(
    body: ForgetPasswordRequest,
    uow_factory: UoWFactory,
    token_repo: TokenRepoDep,
    events: EventPublisherDep,
) -> Response:
    handler = ForgetPasswordHandler(uow_factory(), token_repo, events)
    try:
        await handler.handle(ForgetPasswordCommand(email=body.email))
    except InvalidEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/password/reset",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset password with token",
)
async def reset_password(
    body: ResetPasswordRequest,
    uow_factory: UoWFactory,
    hasher: PasswordHasherDep,
    token_repo: TokenRepoDep,
) -> Response:
    handler = ResetPasswordHandler(uow_factory(), hasher, token_repo)
    try:
        await handler.handle(
            ResetPasswordCommand(
                verify_token=body.verify_token,
                new_password=body.new_password,
            )
        )
    except InvalidVerificationTokenError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except InvalidPasswordError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        )
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change password (authenticated)",
)
async def set_password(
    body: SetPasswordRequest,
    uow_factory: UoWFactory,
    sessions: SessionRepoDep,
    decoder: TokenDecoderDep,
    encoder: TokenEncoderDep,
    hasher: PasswordHasherDep,
    authorization: Annotated[str | None, Header()] = None,
) -> Response:
    token = _bearer(authorization)
    handler = SetPasswordHandler(uow_factory(), sessions, decoder, encoder, hasher)
    try:
        await handler.handle(
            SetPasswordCommand(
                access_token=token,
                new_password=body.new_password,
                device=body.device,
            )
        )
    except DeviceMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except TokenInfrastructureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except InvalidPasswordError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sessions/revoke",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a specific session",
)
async def revoke_session(
    body: RevokeSessionRequest,
    sessions: SessionRepoDep,
    decoder: TokenDecoderDep,
    encoder: TokenEncoderDep,
    authorization: Annotated[str | None, Header()] = None,
) -> Response:
    token = _bearer(authorization)
    handler = RevokeSessionHandler(sessions, decoder, encoder)
    try:
        await handler.handle(
            RevokeSessionCommand(
                access_token=token,
                session_id=body.session_id,
                device=body.device,
            )
        )
    except PermissionDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except DeviceMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except TokenInfrastructureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/sessions/revoke-others",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke all other sessions",
)
async def revoke_all_other(
    body: RevokeAllOtherRequest,
    sessions: SessionRepoDep,
    decoder: TokenDecoderDep,
    encoder: TokenEncoderDep,
    authorization: Annotated[str | None, Header()] = None,
) -> Response:
    token = _bearer(authorization)
    handler = RevokeAllOtherSessionsHandler(sessions, decoder, encoder)
    try:
        await handler.handle(
            RevokeAllOtherSessionsCommand(access_token=token, device=body.device)
        )
    except DeviceMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except TokenInfrastructureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/token/refresh",
    response_model=AccessTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotate access (and optionally refresh) tokens",
)
async def rotate_tokens(
    body: RotateTokensRequest,
    sessions: SessionRepoDep,
    decoder: TokenDecoderDep,
    encoder: TokenEncoderDep,
) -> AccessTokenResponse:
    handler = RotateTokensHandler(sessions, decoder, encoder)
    try:
        result = await handler.handle(
            RotateTokensCommand(refresh_token=body.refresh_token, device=body.device)
        )
    except DeviceMismatchError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except SessionNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    except TokenInfrastructureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return AccessTokenResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )
