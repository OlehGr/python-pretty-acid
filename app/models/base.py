import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry

mapper_registry = registry(metadata=MetaData())


class BaseModel(DeclarativeBase):
    __abstract__ = True

    registry = mapper_registry
    metadata = mapper_registry.metadata

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        unique=True,
    )
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime | None]

    @staticmethod
    def gen_native_utc_now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    @classmethod
    def gen_base_properties(cls) -> dict[str, Any]:
        return {
            "id": uuid.uuid4(),
            "created_at": cls.gen_native_utc_now(),
            "updated_at": None,
        }
