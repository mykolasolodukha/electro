import asyncio
import re
import textwrap

import discord

from ..settings import settings
from .loguru_logging import logger

__MESSAGE_SEPARATOR_ENABLED = False  # a flag that indicates whether the message separator is enabled


# region Redefine `discord`'s `Messageable.sleep` method
async def _message_sleep(self: discord.abc.Messageable, message_text: str) -> None:
    """Sleep for a certain amount of time, depending on the message length."""
    # Get sleep time
    sleep_time = len(message_text) * settings.SLEEP_TIME_PER_CHARACTER if message_text else settings.DEFAULT_SLEEP_TIME

    # Sleep
    await asyncio.sleep(sleep_time)


async def send(
        self,
        content=None,
        *,
        tts=None,
        embed=None,
        embeds=None,
        file=None,
        files=None,
        stickers=None,
        delete_after=None,
        nonce=None,
        allowed_mentions=None,
        reference=None,
        mention_author=None,
        view=None,
        suppress=None,
        silent=None,
):
    """Send a message to the channel."""
    total_sleep_time_at_the_end = 0

    if content and isinstance(content, str):
        message_parts = [
            wrapped_part
            for part in content.split(settings.MESSAGE_BREAK)
            for wrapped_part in textwrap.wrap(
                part, settings.MESSAGE_MAX_LENGTH, replace_whitespace=False, break_long_words=False
            )
        ]

        # Get from the last message part to the first, select all the parts that contain only sleep
        # instructions, and increase the `total_sleep_time_at_the_end` variable
        while message_parts and re.match(rf"^{settings.MESSAGE_SLEEP_INSTRUCTION_PATTERN}$", message_parts[-1].strip()):
            total_sleep_time_at_the_end += float(
                re.search(settings.MESSAGE_SLEEP_INSTRUCTION_PATTERN, message_parts[-1].strip()).group(1)
            )
            message_parts.pop()

        while len(message_parts) > 1:
            message_part = message_parts.pop(0).strip()

            # Sleep
            await _message_sleep(self, message_part)

            # Check if the message contains a sleep instruction
            if match := (re.search(settings.MESSAGE_SLEEP_INSTRUCTION_PATTERN, message_part)):
                sleep_time = float(match.group(1))
                await asyncio.sleep(sleep_time)

                # Remove the sleep instruction from the message
                message_part = re.sub(settings.MESSAGE_SLEEP_INSTRUCTION_PATTERN, "", message_part).strip()

                if not message_part:
                    continue

            # Send the message
            try:
                await discord.abc.Messageable.old_send(
                    self,
                    content=message_part,
                )
            except discord.errors.HTTPException as e:
                logger.error(f"Failed to send a message: {e}")

        content = message_parts[0].strip()

        # Check if the message contains a sleep instruction
        if match := (re.search(settings.MESSAGE_SLEEP_INSTRUCTION_PATTERN, content)):
            sleep_time = float(match.group(1))
            await asyncio.sleep(sleep_time)

            # Remove the sleep instruction from the message
            content = re.sub(settings.MESSAGE_SLEEP_INSTRUCTION_PATTERN, "", content).strip()

        await _message_sleep(self, content)

    # Send the message
    # noinspection PyArgumentList
    sent_message = await discord.abc.Messageable.old_send(
        self,
        content=content,
        tts=tts,
        embed=embed,
        embeds=embeds,
        file=file,
        files=files,
        stickers=stickers,
        delete_after=delete_after,
        nonce=nonce,
        allowed_mentions=allowed_mentions,
        reference=reference,
        mention_author=mention_author,
        view=view,
        suppress=suppress,
        silent=silent,
    )

    # Sleep for the total sleep time at the end
    await asyncio.sleep(total_sleep_time_at_the_end)

    return sent_message


def enable_message_separator():
    """Redefine `discord`'s `Messageable.sleep` method."""
    global __MESSAGE_SEPARATOR_ENABLED

    if __MESSAGE_SEPARATOR_ENABLED:
        return

    discord.abc.Messageable.old_send = discord.abc.Messageable.send
    discord.abc.Messageable.send = send

    __MESSAGE_SEPARATOR_ENABLED = True

# endregion
