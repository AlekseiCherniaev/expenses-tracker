from limits.storage import storage_from_string
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def init_rate_limiter(storage_uri: str) -> Limiter:
    limiter._storage_uri = storage_uri
    limiter._storage = storage_from_string(storage_uri)
    return limiter
