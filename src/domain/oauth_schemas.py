from fastapi.security import OAuth2PasswordBearer

from src.core.config import settings

oauth2_token_schema = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    scopes=settings.parsed_scopes
)
