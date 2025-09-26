from abc import ABC, abstractmethod


class IAvatarStorage(ABC):
    @abstractmethod
    def generate_upload_url(self, user_id: int, ext: str) -> str:
        pass

    @abstractmethod
    def get_public_url(self, key: str) -> str:
        pass
