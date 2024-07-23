import typing

from .storage_buckets import PostgresStorageBucketElement
from ..models import BaseModel

VALUE = typing.TypeVar("VALUE", bound=BaseModel)


class ModelsStorageElement(PostgresStorageBucketElement[VALUE]):
    """Storage element for the models."""

    async def get_data(self, default: VALUE | None = None) -> VALUE | None:
        queryset = await super().get_data(default)

        return await queryset
