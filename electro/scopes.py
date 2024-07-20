from enum import Enum


class FlowScopes(str, Enum):
    """The possible scopes for the Flow."""

    USER = "user"
    CHANNEL = "channel"
    # TODO: [23.10.2023 by Mykola] Allow having guild storage buckets
    # GUILD = "guild"
