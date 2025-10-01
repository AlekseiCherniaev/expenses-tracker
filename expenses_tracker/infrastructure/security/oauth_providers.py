from authlib.integrations.starlette_client import OAuth

from expenses_tracker.core.settings import get_settings

oauth = OAuth()  # type: ignore

oauth.register(
    name="google",
    client_id=get_settings().google_client_id,
    client_secret=get_settings().google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

oauth.register(
    name="github",
    client_id=get_settings().github_client_id,
    client_secret=get_settings().github_client_secret,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "user:email"},
)
