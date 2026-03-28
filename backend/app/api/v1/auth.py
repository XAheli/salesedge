"""Authentication endpoints — register and login."""
from __future__ import annotations

from datetime import datetime, timedelta

import bcrypt
from fastapi import APIRouter, HTTPException, status
from jose import jwt
from pydantic import BaseModel, Field
from sqlmodel import select

from app.config import get_settings
from app.dependencies import DBSession
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "Admin"
    organization: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    token: str
    user: UserInfo


class UserInfo(BaseModel):
    id: str
    name: str
    email: str
    role: str
    organization: str | None
    initials: str


class OnboardingStatus(BaseModel):
    """Whether the user has completed onboarding (required profile fields)."""

    complete: bool
    missing_steps: list[str] = Field(default_factory=list)


def _create_token(user_id: str, email: str) -> str:
    settings = get_settings()
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _initials(name: str) -> str:
    parts = name.strip().split()
    return "".join(p[0] for p in parts if p).upper()[:2] or "SE"


def _user_to_info(user: User) -> UserInfo:
    return UserInfo(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role,
        organization=user.organization,
        initials=_initials(user.name),
    )


@router.post("/register", response_model=APIResponse[AuthResponse])
async def register(req: RegisterRequest, db: DBSession) -> APIResponse[AuthResponse]:
    existing = await db.exec(select(User).where(User.email == req.email))
    if existing.first():
        raise HTTPException(status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=req.name,
        email=req.email,
        hashed_password=_hash_password(req.password),
        role=req.role,
        organization=req.organization,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = _create_token(user.id, user.email)
    return APIResponse(
        data=AuthResponse(
            token=token,
            user=_user_to_info(user),
        ),
    )


@router.post("/login", response_model=APIResponse[AuthResponse])
async def login(req: LoginRequest, db: DBSession) -> APIResponse[AuthResponse]:
    result = await db.exec(select(User).where(User.email == req.email))
    user = result.first()
    if not user or not _verify_password(req.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = _create_token(user.id, user.email)
    return APIResponse(
        data=AuthResponse(
            token=token,
            user=_user_to_info(user),
        ),
    )


@router.get("/me", response_model=APIResponse[UserInfo])
async def get_me(
    db: DBSession,
    current: CurrentUser,
) -> APIResponse[UserInfo]:
    """Return the authenticated user from the JWT."""
    result = await db.exec(select(User).where(User.id == current["user_id"]))
    user = result.first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return APIResponse(data=_user_to_info(user))


@router.get("/onboarding", response_model=APIResponse[OnboardingStatus])
async def onboarding_check(
    db: DBSession,
    current: CurrentUser,
) -> APIResponse[OnboardingStatus]:
    """Return whether required onboarding fields are set (e.g. organization)."""
    result = await db.exec(select(User).where(User.id == current["user_id"]))
    user = result.first()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User not found")

    missing: list[str] = []
    if not (user.organization and user.organization.strip()):
        missing.append("organization")

    return APIResponse(
        data=OnboardingStatus(complete=len(missing) == 0, missing_steps=missing),
    )
