__all__ = ["Link", "LinkSchema"]

from datetime import UTC, datetime

from pydantic import Field
from pymongo import IndexModel

from src.pydantic_base import BaseSchema
from src.storages.mongo.__base__ import CustomDocument


class LinkSchema(BaseSchema):
    slug: str
    form_url: str
    owner_innohassle_id: str
    created_at: datetime


class Link(LinkSchema, CustomDocument):
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    class Settings:
        indexes = [
            IndexModel("slug", unique=True),
            IndexModel("owner_innohassle_id"),
            IndexModel([("owner_innohassle_id", 1), ("form_url", 1)], unique=True),
        ]
