import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='C:/Users/User/PycharmProjects/autozen-api-gateway/src/.env')


class Settings:
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8001')
    USER_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8002')
    SCOPES = os.getenv("SCOPES", "")

    JWT_PUBLIC_SECRET_KEY = os.environ.get('JWT_PUBLIC_SECRET_KEY')
    JWT_ALGORITHM = os.environ.get('ALGORITHM')

    RABBITMQ_LOGIN = os.getenv('RABBITMQ_LOGIN')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
    RABBITMQ_PORT = os.getenv('RABBITMQ_PORT')

    print(JWT_PUBLIC_SECRET_KEY)

    @property
    def parsed_scopes(self) -> dict:
        scopes_dict = {}
        for scope in self.SCOPES.split(','):
            scope_name, scope_description = scope.split(':')
            scopes_dict[scope_name.strip()] = scope_description.strip()

        return scopes_dict

    @property
    def rabbitmq_url(self) -> str:
        return f'amqp://{self.RABBITMQ_LOGIN}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/'


settings = Settings()
