"""Schemas relacionados ao usuário autenticado."""

from pydantic import BaseModel


class UserOut(BaseModel):
    email: str
    name: str
    picture: str | None = None
    hd: str | None = None
