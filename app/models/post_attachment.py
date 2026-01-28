import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class PostAttachment(BaseModel):
    __tablename__ = "post_attachment"

    file_url: Mapped[str]
    post_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("post.id"))

    @classmethod
    def create(cls, *, file_url: str, post_id: uuid.UUID) -> "PostAttachment":
        return PostAttachment(
            **cls.gen_base_properties(), file_url=file_url, post_id=post_id
        )
