from sqlalchemy.orm import Mapped

from .base import BaseModel


class User(BaseModel):
    __tablename__ = "user"

    name: Mapped[str]
    posts_count: Mapped[int]

    @classmethod
    def create(cls, *, name: str) -> "User":
        return User(**cls.gen_base_properties(), name=name, posts_count=0)

    def update_posts_count(self, count: int) -> None:
        self.posts_count = count
        self._on_update()

    def _on_update(self) -> None:
        self.updated_at = self.gen_native_utc_now()
