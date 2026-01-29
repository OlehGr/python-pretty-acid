import uuid

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel


class Post(BaseModel):
    __tablename__ = "post"

    text: Mapped[str]
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    attachments_count: Mapped[int]

    @classmethod
    def create(cls, *, text: str, user_id: uuid.UUID) -> "Post":
        return Post(
            **cls.gen_base_properties(), text=text, user_id=user_id, attachments_count=0
        )

    def _on_update(self) -> None:
        self.updated_at = self.gen_native_utc_now()

    def update_attachments_count(self, count: int) -> None:
        self.attachments_count = count
        self._on_update()
