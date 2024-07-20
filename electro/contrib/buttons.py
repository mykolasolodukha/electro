"""The buttons that can be used in the `electro` Framework."""

import typing

import discord.ui

from ..flow_connector import FlowConnector
from ..flow_step import BaseFlowStep

CALLBACK_TYPE = typing.Callable[[FlowConnector], typing.Awaitable[None]] | BaseFlowStep


class ActionButton(discord.ui.Button):
    """A button that performs an action when clicked."""

    action_callback: CALLBACK_TYPE

    def __init__(self, label: str, action_callback: CALLBACK_TYPE, *args, **kwargs):
        """Initialize the `ActionButton`."""
        super().__init__(label=label, *args, **kwargs)

        if isinstance(action_callback, BaseFlowStep):
            if action_callback.non_blocking:
                raise ValueError(
                    "Non-blocking steps cannot be used as action callbacks because 'non-blocking' would be ignored."
                )

        self.action_callback = action_callback

    async def trigger_action(self, flow_connector: FlowConnector):
        """Trigger the `ActionButton`."""
        if isinstance(self.action_callback, BaseFlowStep):
            await self.action_callback.run(flow_connector)
        else:
            await self.action_callback(flow_connector)
