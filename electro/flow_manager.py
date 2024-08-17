"""Flow Manager, the main object that manages all the `Flow`s."""

import typing
from collections import defaultdict

import discord

from ._common import ContextInstanceMixin
from .flow import Flow, FlowConnector, FlowFinished
from .flow_connector import FlowConnectorEvents

# from decorators import fail_safely
from .models import Channel, User
from .scopes import FlowScopes
from .storage import BaseFlowStorage, ChannelData, FlowMemoryStorage, UserData
from .toolkit.loguru_logging import logger
from .toolkit.tortoise_orm import Model


class EventCannotBeProcessed(Exception):
    """The exception that is raised when the event cannot be processed."""

    pass


class FlowManager(ContextInstanceMixin):
    """The main object that manages all the `Flow`s."""

    _storage__user_model: Model = User
    _storage__channel_model: Model = Channel

    def __init__(
        self,
        bot: discord.Bot,
        flows: typing.Optional[list[Flow]] = None,
        storage: typing.Optional[BaseFlowStorage] = None,
        on_finish_callbacks: typing.Optional[list[typing.Callable[[FlowConnector], typing.Awaitable[None]]]] = None,
    ):
        self.bot = bot
        self.flows: list[Flow] = flows

        self.storage = storage or FlowMemoryStorage()

        self._on_finish_callbacks: list[typing.Callable[[FlowConnector], typing.Awaitable[None]]] = (
            on_finish_callbacks or []
        )

        # Set the current flow manager
        self.set_current(self)

    # region User State and Data management
    async def _get_user_state(self, user: discord.User) -> str | None:
        """Get the state of the user."""
        return await self.storage.get_user_state(user.id)

    async def _set_user_state(self, user: discord.User, state: str | None):
        """Set the state of the user."""
        await self.storage.set_user_state(user.id, state)

    async def _delete_user_state(self, user: discord.User):
        """Delete the state of the user."""
        await self.storage.delete_user_state(user.id)

    async def _get_user_data(self, user: discord.User) -> UserData:
        """Get the data of the user."""
        return await self.storage.get_user_data(user.id)

    async def _set_user_data(self, user: discord.User, data: UserData | dict[str, typing.Any] | None):
        """Set the data of the user."""
        await self.storage.set_user_data(user.id, data)

    async def _delete_user_data(self, user: discord.User):
        """Delete the data of the user."""
        await self.storage.delete_user_data(user.id)

    # endregion

    # region Channel State and Data management
    async def _get_channel_state(self, channel: discord.TextChannel) -> str | None:
        """Get the state of the channel."""
        return await self.storage.get_channel_state(channel.id)

    async def _set_channel_state(self, channel: discord.TextChannel, state: str | None):
        """Set the state of the channel."""
        await self.storage.set_channel_state(channel.id, state)

    async def _delete_channel_state(self, channel: discord.TextChannel):
        """Delete the state of the channel."""
        await self.storage.delete_channel_state(channel.id)

    async def _get_channel_data(self, channel: discord.TextChannel) -> ChannelData:
        """Get the data of the channel."""
        return await self.storage.get_channel_data(channel.id)

    async def _set_channel_data(self, channel: discord.TextChannel, data: ChannelData | dict[str, typing.Any] | None):
        """Set the data of the channel."""
        await self.storage.set_channel_data(channel.id, data)

    async def _delete_channel_data(self, channel: discord.TextChannel):
        """Delete the data of the channel."""
        await self.storage.delete_channel_data(channel.id)

    # endregion

    # region Get Flow
    def get_flow(self, flow_name: str) -> Flow | None:
        """Get the flow by its name."""
        for flow in self.flows:
            if flow.__class__.__name__ == flow_name:
                return flow

        return None

    # endregion

    async def _create_user_and_channel(
        self, user: discord.User | None = None, channel: discord.TextChannel | discord.DMChannel | None = None
    ):
        """Create the `User` and `Channel` records if they don't exist."""
        logger.info(f"Creating the User and Channel records for {user=}, {channel=}")

        user_id = getattr(user, "id", None) if user else None
        channel_id = getattr(channel, "id", None) if channel else None

        logger.debug(f"Creating the User and Channel records for {user_id=} and {channel_id=}")

        if user and not user_id:
            logger.warning(f"Failed to get the user ID: {user=}, {channel=}, {channel_id=}")

        if channel and not channel_id:
            logger.warning(f"Failed to get the channel ID: {channel=}, {user=}, {user_id=}")

        # Create the User record
        if user_id and not await self._storage__user_model.get_or_none(id=user_id):
            await self._storage__user_model.create(
                id=user_id,
                username=user.name,
                discriminator=user.discriminator,
                avatar=user.avatar.url if user.avatar else None,
            )
            logger.info(
                f"Created the User record for {user_id=}, "
                f"{getattr(user, 'name')=}, and {getattr(user, 'display_name')=}"
            )

        # Create the Channel record
        if channel_id and not await self._storage__channel_model.get_or_none(id=channel_id):
            await self._storage__channel_model.create(
                id=channel_id,
                name=getattr(channel, "name", None),
                guild_id=getattr(getattr(channel, "guild", None), "id", None),
                type=channel.type,
            )

            logger.info(
                f"Created the Channel record for {channel_id=}, "
                f"{getattr(channel, 'name', None)=}, {getattr(channel, 'type')=}"
            )

    # TODO: [2024-07-19 by Mykola] Use the decorators
    # @fail_safely
    async def _dispatch(self, flow_connector: FlowConnector):
        """Dispatch the flow."""
        # Create the User and Channel records if they don't exist
        await self._create_user_and_channel(flow_connector.user, flow_connector.channel)

        is_dm_channel = flow_connector.channel and flow_connector.channel.type == discord.ChannelType.private

        if is_dm_channel:
            scope = FlowScopes.USER
        else:
            scope = FlowScopes.CHANNEL
        # TODO: [17.05.2024 by Mykola] Allow for `FlowScopes.GUILD` flows

        # Check whether this event has triggered any of the flows
        for flow in self.flows:
            # Check all the triggers
            if await flow.check_triggers(flow_connector, scope=scope):
                await flow.run(flow_connector)
                break

        else:
            # Check if it's not something that shouldn't be handled by the flows
            if (
                flow_connector.event == FlowConnectorEvents.MESSAGE
                and flow_connector.message.content
                and flow_connector.message.content.startswith(flow_connector.bot.command_prefix)
            ):
                if scope == FlowScopes.USER:
                    # Remove user's state, so that the user wouldn't resume any flow
                    await self.storage.delete_user_state(flow_connector.user.id)

                    raise EventCannotBeProcessed(
                        f"The message is a command that is not handled by any of the flows: "
                        f"{flow_connector.message.content}"
                    )
                else:
                    logger.warning(
                        "Out-of-scope `{scope}` command `{flow_connector.message.content}` is not handled by the flows",
                        scope=scope,
                        flow_connector=flow_connector,
                    )
                    raise EventCannotBeProcessed(
                        f"Out-of-scope `{scope}` command `{flow_connector.message.content}` is not handled by the flows"
                    )

            # Get all the flows that can be run:
            # Check if the flow can be run (maybe the user is in the middle of the flow)
            flows_that_can_be_run = [flow for flow in self.flows if await flow.check(flow_connector, scope=scope)]

            # If this event has not triggered any of the flows,
            # check if the user is in the middle of the flow, and if so, continue it

            # If there are multiple flows that can be run, decide which one gets the priority based on the scope
            if len(flows_that_can_be_run) > 1:
                flows_by_scope = defaultdict(list)
                for flow in flows_that_can_be_run:
                    # noinspection PyProtectedMember
                    flows_by_scope[flow._scope].append(flow)

                # If it's not a private channel, Channel-scoped flows get the priority
                if flow_connector.channel.type != discord.ChannelType.private and (
                    channel_scope_flows := flows_by_scope.get(FlowScopes.CHANNEL)
                ):
                    flows_that_can_be_run = channel_scope_flows

            for flow in flows_that_can_be_run:
                try:
                    logger.info(f"Running the flow {flow} for {flow_connector.user.id}")
                    await flow.step(flow_connector)
                except FlowFinished:
                    # TODO: [28.08.2023 by Mykola] Go to the next flow?
                    # Delete the state and data for the user
                    await self.storage.delete_user_state(flow_connector.user.id)
                    await self.storage.delete_user_data(flow_connector.user.id)

                    # Run the callbacks
                    for callback in self._on_finish_callbacks:
                        await callback(flow_connector)

                # TODO: [16.03.2024 by Mykola] Maybe allow running multiple flows at the same time?
                break  # Do not allow running multiple flows at the same time
            else:
                if scope == FlowScopes.USER:
                    logger.warning(f"Received an event that cannot be processed: {flow_connector.event}")
                    raise EventCannotBeProcessed(f"Received an event that cannot be processed: {flow_connector.event}")
                else:
                    logger.debug(
                        "Out-of-scope `{scope}` event cannot be processed: "
                        "`{flow_connector.event}` in `#{flow_connector.channel}`",
                        scope=scope,
                        flow_connector=flow_connector,
                    )
                    return  # Do not raise an exception, as it's not an error

    async def dispatch(self, flow_connector: FlowConnector):
        """Dispatch the flow."""
        # Set the current flow connector
        FlowConnector.set_current(flow_connector)

        async with self:
            return await self._dispatch(flow_connector)

    async def on_message(self, message: discord.Message):
        """Handle the messages sent by the users."""

        # Ignore the messages sent by the bots
        if message.author.bot:
            return

        # Get the user state and data
        # TODO: [20.08.2023 by Mykola] Use context manager for this
        logger.info(f"Getting the user state and data for {message.author.id}")
        user_state = await self._get_user_state(message.author)
        user_data = await self._get_user_data(message.author)

        # Get the channel state and data
        channel_state = await self._get_channel_state(message.channel)
        channel_data = await self._get_channel_data(message.channel)

        flow_connector = FlowConnector(
            flow_manager=self,
            bot=self.bot,
            event=FlowConnectorEvents.MESSAGE,
            user=message.author,
            channel=message.channel,
            message=message,
            user_state=user_state,
            user_data=user_data,
            channel_state=channel_state,
            channel_data=channel_data,
        )

        return await self.dispatch(flow_connector)

    async def on_interaction(self, interaction: discord.Interaction):
        """Handle the interactions sent by the users."""
        # Get the user state and data
        logger.info(f"Getting the user state and data for {interaction.user.id}")
        user_state = await self._get_user_state(interaction.user)
        user_data = await self._get_user_data(interaction.user)

        # Get the channel state and data
        channel_state = await self._get_channel_state(interaction.message.channel)
        channel_data = await self._get_channel_data(interaction.message.channel)

        # noinspection PyTypeChecker
        flow_connector = FlowConnector(
            flow_manager=self,
            bot=self.bot,
            event=FlowConnectorEvents.BUTTON_CLICK,
            user=interaction.user,
            channel=interaction.channel,
            user_state=user_state,
            user_data=user_data,
            message=interaction.message,
            interaction=interaction,
            channel_state=channel_state,
            channel_data=channel_data,
        )

        return await self.dispatch(flow_connector)

    async def on_member_join(self, member: discord.Member):
        """Handle the `member_join` event."""
        # Get the user state and data
        logger.info(f"Getting the user state and data for {member.id}")
        # TODO: [22.08.2023 by Mykola] Use correct types here
        user_state = await self._get_user_state(member)
        user_data = await self._get_user_data(member)

        # noinspection PyProtectedMember
        flow_connector = FlowConnector(
            flow_manager=self,
            bot=self.bot,
            event=FlowConnectorEvents.MEMBER_JOIN,
            user=member._user,
            member=member,
            # TODO: [28.08.2023 by Mykola] Use the correct channel here
            channel=member.guild.system_channel,
            message=None,
            user_state=user_state,
            user_data=user_data,
            channel_state=None,
            channel_data=ChannelData(),
        )

        return await self.dispatch(flow_connector)

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Handle the `member_join` event."""
        # Get the user state and data
        logger.info(f"Getting the user state and data for {after.id}")
        user_state = await self._get_user_state(after)
        user_data = await self._get_user_data(after)

        # noinspection PyProtectedMember
        flow_connector = FlowConnector(
            flow_manager=self,
            bot=self.bot,
            event=FlowConnectorEvents.MEMBER_UPDATE,
            user=after._user,
            member=after,
            channel=after.guild.system_channel,
            message=None,
            user_state=user_state,
            user_data=user_data,
            extra_data={"old_member": before},
            channel_state=None,
            channel_data=ChannelData(),
        )

        return await self.dispatch(flow_connector)

    # region Context Manager
    async def __aenter__(self):
        """Enter the context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        flow_connector = FlowConnector.get_current()

        # After the flow step(s) is/are run, update the user state and data
        if flow_connector.user:
            await self._set_user_state(flow_connector.user, flow_connector.user_state)
            await self._set_user_data(flow_connector.user, flow_connector.user_data)

        # Also, update the channel state and data
        if flow_connector.channel:
            await self._set_channel_state(flow_connector.channel, flow_connector.channel_state)
            await self._set_channel_data(flow_connector.channel, flow_connector.channel_data)

    # endregion
