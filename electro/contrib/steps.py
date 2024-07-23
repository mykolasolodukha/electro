import typing
from dataclasses import dataclass
from typing import Type

import discord
from electro import FlowConnector
from electro.contrib.storage_buckets import BaseStorageBucketElement

from .storages import ModelsStorageElement
from .views import ChooseOneOptionView
from ..flow_step import MessageFlowStep
from ..models import BaseModel


class ChooseOneModelView(ChooseOneOptionView):
    """Choose one of the models."""

    def __init__(self, model_to_choose_from: Type[BaseModel],
                 options: list[str | discord.ui.Button] | typing.Callable[[], typing.Awaitable[list[str]]] = None,
                 answers_storage: BaseStorageBucketElement | None = None, **kwargs):
        """Initialize the view."""
        if not options:
            options = []

        super().__init__(options, answers_storage, **kwargs)

        self.model_to_choose_from: Type[BaseModel] = model_to_choose_from

    async def _get_instances_pks(self) -> list[str]:
        instances: list[BaseModel] = await self.model_to_choose_from.filter(is_active=True, is_deleted=False).all()

        return [str(instance.pk) for instance in instances]

    async def get_static_buttons(self, flow_connector: FlowConnector) -> list[str]:
        return await self._get_instances_pks() + await super().get_static_buttons(flow_connector)

    async def _set_user_answer(self, user_answer: typing.Any):
        """Set the user answer."""
        instance: BaseModel = await self.model_to_choose_from.get_or_none(pk=user_answer)

        return await super()._set_user_answer(instance)


@dataclass
class ChooseOneFromModelsStep(MessageFlowStep):
    """Choose one of the models."""

    model_to_choose_from: Type[BaseModel] = None

    storage_to_save_model_to: ModelsStorageElement = None

    def __post_init__(self):
        if self.model_to_choose_from is None:
            raise ValueError("`model_to_choose_from` is required!")
        if self.storage_to_save_model_to is None:
            raise ValueError("`storage_to_save_model_to` is required!")

        self.view = ChooseOneModelView(
            model_to_choose_from=self.model_to_choose_from,
            answers_storage=self.storage_to_save_model_to,
        )
