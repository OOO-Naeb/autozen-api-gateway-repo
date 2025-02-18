import uvicorn
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.middleware.exceptions_middleware import ExceptionMiddleware
from src.presentation.api.v1.auth_routes import auth_router
from src.presentation.api.v1.payment_routes import payment_router

app = FastAPI()

# Routers
app.include_router(auth_router)
app.include_router(payment_router)

# Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=ExceptionMiddleware(app=app).dispatch)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
