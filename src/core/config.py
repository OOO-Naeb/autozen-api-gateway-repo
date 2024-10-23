import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='C:/Users/User/PycharmProjects/autozen-api-gateway/src/.env')


class Settings:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ALGORITHM = os.environ.get('ALGORITHM')
    ACCESS_TOKEN_EXPIRE_MINUTES = os.environ.get('ACCESS_TOKEN_EXPIRE_MINUTES')
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8001')
    USER_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8002')
    SCOPES = os.getenv("SCOPES", "")

    @property
    def get_parsed_scopes(self):
        scopes_dict = {}
        for scope in self.SCOPES.split(','):
            scope_name, scope_description = scope.split(':')
            scopes_dict[scope_name.strip()] = scope_description.strip()

        return scopes_dict


settings = Settings()
