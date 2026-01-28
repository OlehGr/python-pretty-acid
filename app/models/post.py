import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Post(BaseModel):
    __tablename__ = "post"

    text: Mapped[str]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))

    @classmethod
    def create(cls, *, text: str, user_id: uuid.UUID) -> "Post":
        return Post(**cls.gen_base_properties(), text=text, user_id=user_id)
