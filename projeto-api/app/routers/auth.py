"""Rotas OAuth Google + /me + /logout."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from app.auth import build_oauth, validate_google_user
from app.config import get_settings
from app.deps import CurrentUser
from app.schemas.user import UserOut

router = APIRouter(tags=["auth"])
_oauth = build_oauth()


@router.get("/login")
async def login(request: Request) -> RedirectResponse:
    settings = get_settings()
    google = _oauth.create_client("google")
    if google is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OAuth não configurado",
        )
    return await google.authorize_redirect(
        request,
        settings.oauth_redirect_uri,
        hd=settings.allowed_domain,
    )


@router.get("/auth/callback")
async def auth_callback(request: Request) -> RedirectResponse:
    google = _oauth.create_client("google")
    if google is None:
        raise HTTPException(status_code=500, detail="OAuth não configurado")

    token = await google.authorize_access_token(request)
    userinfo: dict[str, Any] = token.get("userinfo") or {}
    if not userinfo:
        raise HTTPException(status_code=400, detail="userinfo ausente no token")

    user = validate_google_user(userinfo)
    request.session["user"] = user

    origins = get_settings().cors_origins_list
    target = origins[0] if origins else "/"
    return RedirectResponse(url=target)


@router.post("/logout")
async def logout(request: Request) -> dict[str, str]:
    request.session.clear()
    return {"status": "logged_out"}


@router.get("/api/me", response_model=UserOut)
async def me(user: CurrentUser) -> UserOut:
    return UserOut(
        email=user["email"],
        name=user.get("name", ""),
        picture=user.get("picture"),
        hd=user.get("hd"),
    )
