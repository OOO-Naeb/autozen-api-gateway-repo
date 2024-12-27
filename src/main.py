import uvicorn
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.middleware.exception_middleware import ExceptionMiddleware
from src.presentation.api.v1.auth_routes import auth_router

app = FastAPI()

# Routers
app.include_router(auth_router)

# Middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=ExceptionMiddleware(app=app).dispatch)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
