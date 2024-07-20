"""The substitutions' module. Used to substitute the variables in all the `TemplatedString`s."""

from __future__ import annotations

import typing
from abc import ABC, abstractmethod

import discord

from .toolkit.redis_storage import RedisStorage

from .flow_connector import FlowConnector

REDIS_STORAGE_VALUE = typing.TypeVar("REDIS_STORAGE_VALUE", bound=typing.Any)


RETURN_TYPE = typing.TypeVar("RETURN_TYPE")


class BaseSubstitution(ABC, typing.Generic[RETURN_TYPE]):
    """The base class for the substitution objects."""

    @abstractmethod
    async def resolve(self, connector: FlowConnector) -> RETURN_TYPE:
        """Resolve the substitution object."""
        raise NotImplementedError


class ManualRedisStorageSubstitution(BaseSubstitution):
    """The Substitution object that requests the data from the Redis storage."""

    redis_storage: RedisStorage
    redis_storage_key_name: str

    formatter: typing.Callable[[REDIS_STORAGE_VALUE], str] | None = None

    is_chat_specific: bool = False

    def __init__(
        self,
        redis_storage: RedisStorage,
        redis_storage_key_name: str,
        default_value: typing.Optional[REDIS_STORAGE_VALUE] = None,
        formatter: typing.Callable[[REDIS_STORAGE_VALUE], str] | None = None,
        is_chat_specific: bool = False,
    ):
        self.redis_storage = redis_storage
        self.redis_storage_key_name = redis_storage_key_name
        self.default_value = default_value
        self.formatter = formatter
        self.is_chat_specific = is_chat_specific

    async def resolve(self, connector: FlowConnector) -> str:
        if not self.is_chat_specific and not isinstance(connector.channel, discord.DMChannel):
            channel = await connector.bot.create_dm(connector.user)
        else:
            channel = connector.channel

        try:
            redis_user_data: dict[str, typing.Any] = (
                await self.redis_storage.get_data(
                    chat=channel.id,
                    user=connector.user.id,
                )
                or {}
            )
            data: REDIS_STORAGE_VALUE = redis_user_data.get(self.redis_storage_key_name, self.default_value)
        except (TypeError, IndexError) as exception:
            return str(f"{exception} in REDIS STORAGE SUBSTITUTION for key: {self.redis_storage_key_name}")
        else:
            if self.formatter:
                return self.formatter(data)
            else:
                return str(data)


class AttributeSubstitution(BaseSubstitution):
    substitution_object: BaseFlowSubstitutionObject
    attribute: str | None = None

    def __init__(self, substitution_object: BaseFlowSubstitutionObject, attribute: str | None = None):
        self.substitution_object = substitution_object
        self.attribute = attribute

    async def resolve(self, connector: FlowConnector) -> RETURN_TYPE:
        if self.substitution_object.flow_connector_attribute:
            real_object = getattr(connector, self.substitution_object.flow_connector_attribute)
        else:
            # Should never happen, for now
            real_object = self.substitution_object.object

        if self.attribute:
            return getattr(real_object, self.attribute)
        else:
            return str(real_object)


class CallbackSubstitution(BaseSubstitution[RETURN_TYPE]):
    """The Substitution object that would be fetched from the callback."""

    callback: typing.Callable[[FlowConnector], typing.Awaitable[RETURN_TYPE]]

    def __init__(self, callback: typing.Callable[[FlowConnector], typing.Awaitable[RETURN_TYPE]]):
        self.callback = callback

    async def resolve(self, connector: FlowConnector) -> RETURN_TYPE:
        return await self.callback(connector)


class BaseFlowSubstitutionObject(ABC):
    object: object

    # TODO: [29.08.2023 by Mykola] Make it redundant to specify the attribute
    flow_connector_attribute: str | None = None

    def __getattribute__(self, item) -> AttributeSubstitution:
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return AttributeSubstitution(self, item)


class UserSubstitutionObject(BaseFlowSubstitutionObject):
    object: discord.User

    flow_connector_attribute = "user"


UserObject = UserSubstitutionObject()
