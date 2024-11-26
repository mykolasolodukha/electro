"""The Schemas used by the `electro` API."""

# TODO: [2024-11-26 by Mykola] Make it work not only with Discord, but with other platforms as well.

from pydantic import BaseModel


class DiscordUser(BaseModel):
    """The model for Discord User."""

    id: int
    username: str
    discriminator: str
    avatar: str


class DiscordGuild(BaseModel):
    """The model for Discord Guild."""

    id: int
    name: str
    icon: str | None


class DiscordChannel(BaseModel):
    """The model for Discord Channel."""

    id: int
    name: str | None
    type: str

    guild: DiscordGuild | None

    used_for: str | None


class DiscordMessage(BaseModel):
    """The model for Discord Message."""

    id: int
    content: str

    author: DiscordUser
    channel: DiscordChannel

    created_at: str
    edited_at: str | None
