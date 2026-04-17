"""Dependências compartilhadas."""

from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import current_user
from app.db import get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[dict[str, Any], Depends(current_user)]


async def session_gen() -> AsyncGenerator[AsyncSession, None]:
    async for s in get_session():
        yield s
