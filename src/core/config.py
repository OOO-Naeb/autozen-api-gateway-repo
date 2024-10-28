import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='C:/Users/User/PycharmProjects/autozen-api-gateway/src/.env')


class Settings:
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8001')
    USER_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8002')
    SCOPES = os.getenv("SCOPES", "")

    JWT_PUBLIC_SECRET_KEY = os.environ.get('JWT_PUBLIC_SECRET_KEY')
    JWT_ALGORITHM = os.environ.get('ALGORITHM')

    print(JWT_PUBLIC_SECRET_KEY)

    @property
    def get_parsed_scopes(self):
        scopes_dict = {}
        for scope in self.SCOPES.split(','):
            scope_name, scope_description = scope.split(':')
            scopes_dict[scope_name.strip()] = scope_description.strip()

        return scopes_dict


settings = Settings()
