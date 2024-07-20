"""
This module contains the button styles and a function to create [Discord] buttons.

The idea being, we abstract the button styles and the button creation so that in the future, when
we want to support multiple front-ends, we can do so without needing to change the public interface of the Framework.
"""

import discord


class FrameworkButtonStyle(discord.ButtonStyle):
    """A class to store the button styles."""


def create_button(
    label: str, *, style: FrameworkButtonStyle = FrameworkButtonStyle.primary, custom_id: str = None
) -> discord.ui.Button:
    """Get a button with the given label and style."""
    # TODO: [04.03.2024 by Mykola] Make sure the `FrameworkButtonStyle` is compatible with `discord.ui.Button`
    # Right now we hook it up directly, but since we want to add a new front-end in the future, the way we connect the
    # both might change.
    return discord.ui.Button(label=label, style=style, custom_id=custom_id)
