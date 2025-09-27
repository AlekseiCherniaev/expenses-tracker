from abc import ABC, abstractmethod


class IAvatarStorage(ABC):
    @abstractmethod
    def generate_upload_url(self, object_name: str, expires_in: int = 3600) -> str:
        pass

    @abstractmethod
    def get_public_url(self, object_name: str) -> str:
        pass

    @abstractmethod
    def delete_object(self, object_name: str) -> bool:
        pass
