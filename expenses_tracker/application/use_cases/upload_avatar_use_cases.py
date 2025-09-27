from uuid import UUID, uuid4

from expenses_tracker.application.dto.user import UserDTO
from expenses_tracker.application.interfaces.avatar_storage import IAvatarStorage
from expenses_tracker.application.interfaces.cache_service import ICacheService
from expenses_tracker.core.settings import get_settings
from expenses_tracker.domain.exceptions.user import UserNotFound
from expenses_tracker.domain.repositories.uow import IUnitOfWork


class UserAvatarUseCase:
    def __init__(
        self,
        avatar_storage: IAvatarStorage,
        unit_of_work: IUnitOfWork,
        cache_service: ICacheService[UserDTO],
    ):
        self._avatar_storage = avatar_storage
        self._unit_of_work = unit_of_work
        self._cache_service = cache_service

    @staticmethod
    def _object_name(user_id: UUID) -> str:
        return f"{user_id}/{uuid4()}.png"

    @staticmethod
    def _extract_object_name(url: str) -> str:
        return url.rsplit(f"{get_settings().minio_avatar_bucket}/", 1)[-1]

    @staticmethod
    def _user_cache_key(user_id: UUID) -> str:
        return f"user:{user_id}"

    async def generate_presigned_urls(self, user_id: UUID) -> tuple[str, str]:
        object_name = self._object_name(user_id=user_id)
        upload_url = self._avatar_storage.generate_upload_url(object_name=object_name)
        public_url = self._avatar_storage.get_public_url(object_name=object_name)

        async with self._unit_of_work as uow:
            user = await uow.user_repository.get_by_id(user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")

            await uow.user_repository.update_avatar_url(
                user_id=user_id, avatar_url=public_url
            )
            await self._cache_service.delete(key=self._user_cache_key(user_id))
        return upload_url, public_url

    async def delete_avatar(self, user_id: UUID) -> None:
        async with self._unit_of_work as uow:
            user = await uow.user_repository.get_by_id(user_id)
            if not user:
                raise UserNotFound(f"User with id {user_id} not found")

            if user.avatar_url is not None:
                self._avatar_storage.delete_object(
                    object_name=self._extract_object_name(user.avatar_url)
                )
                await uow.user_repository.update_avatar_url(
                    user_id=user_id, avatar_url=None
                )
                await self._cache_service.delete(key=self._user_cache_key(user_id))
        return None
