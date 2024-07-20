"""The storage buckets for the `GPTAssistantStep`s."""

from abc import ABC

from .storage_buckets import BasePostgresStorageBucket, BaseStorageBucket, StorageBucketElement


class BaseAssistantsStorageBucket(BaseStorageBucket, ABC):
    """Base storage bucket for the `GPTAssistantStep`s."""

    __abstract = True

    thread_id: StorageBucketElement[str]


class BasePostgresAssistantsStorageBucket(BasePostgresStorageBucket, BaseAssistantsStorageBucket):
    """Base storage bucket for the `GPTAssistantStep`s."""

    __abstract = True
