import os
from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

load_dotenv(dotenv_path='C:/Users/User/PycharmProjects/autozen-api-gateway/src/.env')


class Settings(BaseSettings):
    AUTH_SERVICE_URL: str = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8001')
    USER_SERVICE_URL: str = os.getenv('AUTH_SERVICE_URL', 'http://localhost:8002')
    SCOPES: str = os.getenv("SCOPES", "")

    JWT_PUBLIC_SECRET_KEY: str = os.environ.get('JWT_PUBLIC_SECRET_KEY')
    JWT_ALGORITHM: str = os.environ.get('ALGORITHM')

    RABBITMQ_LOGIN: str = os.getenv('RABBITMQ_LOGIN')
    RABBITMQ_PASSWORD: str = os.getenv('RABBITMQ_PASSWORD')
    RABBITMQ_HOST: str = os.getenv('RABBITMQ_HOST')
    RABBITMQ_PORT: int = int(os.getenv('RABBITMQ_PORT'))

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
