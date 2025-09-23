from slowapi import Limiter
from slowapi.util import get_remote_address

from expenses_tracker.core.settings import get_settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=f"redis://{get_settings().redis_host}:{get_settings().redis_port}/{get_settings().redis_db}",
)
