from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core.exceptions import ApiGatewayError
from src.infrastructure.exceptions import AuthServiceError, RabbitMQError


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)

            return response
        except ApiGatewayError as exc:
            if exc.status_code == 401 or exc.status_code == 403:
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"success": False, "message": exc.detail},
                )
        except AuthServiceError as exc:
            if exc.status_code == 401:
                return JSONResponse(
                    status_code=401,
                    content={"success": False, "message": 'Login or password are incorrect.'},
                )
            elif exc.status_code == 403:
                return JSONResponse(
                    status_code=403,
                    content={"success": False, "message": 'User account is inactive.'},
                )
            elif exc.status_code == 404:
                return JSONResponse(
                    status_code=404,
                    content={"success": False, "message": 'User not found.'},
                )
            elif exc.status_code == 500:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": exc.detail},  # TODO: FOR DEBUG ONLY. CHANGE TO A CUSTOM ERROR RESPONSE OTHERWISE.
                )
            elif exc.status_code == 504:
                return JSONResponse(
                    status_code=504,
                    content={
                        "success": False,
                        "message": 'Something went wrong. Please try again later.'
                    },
                )
        except RabbitMQError:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "message": 'Something went wrong. Please try again later.'
                },
            )
        except HTTPException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"success": False, "message": exc.detail},
            )
        except Exception as exc:
            raise exc  # TODO: FOR DEBUG ONLY. CHANGE TO A CUSTOM ERROR RESPONSE OTHERWISE.