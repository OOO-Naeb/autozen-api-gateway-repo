from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings

oauth2_access_token_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    scopes=settings.get_parsed_scopes
)

oauth2_refresh_token_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/refresh",
    scopes=settings.get_parsed_scopes
)
