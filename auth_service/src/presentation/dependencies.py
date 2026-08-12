"""FastAPI dependency injection wiring."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domain.ports.email_blocklist_checker import EmailBlocklistChecker
from src.domain.ports.event_publisher import EventPublisher
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.session_repository import SessionRepository
from src.domain.ports.token_decoder import TokenDecoder
from src.domain.ports.token_encoder import TokenEncoder
from src.domain.ports.unit_of_work import UnitOfWork
from src.domain.ports.verification_token_repository import VerificationTokenRepository
from src.infrastructure.persistence.unit_of_work import SQLAlchemyUnitOfWork
from src.infrastructure.security.bcrypt_password_hasher import BcryptPasswordHasher
from src.infrastructure.security.jwt_token_decoder import JwtTokenDecoder
from src.infrastructure.security.jwt_token_encoder import JwtTokenEncoder


def get_session_factory(request: Request) -> async_sessionmaker[AsyncSession]:
    return request.app.state.session_factory


def get_uow_factory(
    session_factory: Annotated[
        async_sessionmaker[AsyncSession], Depends(get_session_factory)
    ],
) -> Callable[[], UnitOfWork]:
    def factory() -> UnitOfWork:
        return SQLAlchemyUnitOfWork(session_factory)

    return factory


def get_event_publisher(request: Request) -> EventPublisher:
    return request.app.state.event_publisher


def get_session_repository(request: Request) -> SessionRepository:
    return request.app.state.session_repository


def get_verification_token_repository(
    request: Request,
) -> VerificationTokenRepository:
    return request.app.state.verification_token_repository


def get_password_hasher() -> PasswordHasher:
    return BcryptPasswordHasher()


def get_token_encoder() -> TokenEncoder:
    return JwtTokenEncoder()


def get_token_decoder() -> TokenDecoder:
    return JwtTokenDecoder()


def get_email_blocklist(request: Request) -> EmailBlocklistChecker:
    return request.app.state.email_blocklist


UoWFactory = Annotated[Callable[[], UnitOfWork], Depends(get_uow_factory)]
EventPublisherDep = Annotated[EventPublisher, Depends(get_event_publisher)]
SessionRepoDep = Annotated[SessionRepository, Depends(get_session_repository)]
TokenRepoDep = Annotated[
    VerificationTokenRepository, Depends(get_verification_token_repository)
]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
TokenEncoderDep = Annotated[TokenEncoder, Depends(get_token_encoder)]
TokenDecoderDep = Annotated[TokenDecoder, Depends(get_token_decoder)]
EmailBlocklistDep = Annotated[EmailBlocklistChecker, Depends(get_email_blocklist)]
