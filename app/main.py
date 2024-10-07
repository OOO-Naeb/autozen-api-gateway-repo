from typing import Annotated

import uvicorn
from fastapi import FastAPI
from fastapi.params import Depends

from app.interfaces.http.schemas.schemas import AccessToken
from app.interfaces.http.v1.auth_routes import auth_router
from app.interfaces.services.auth_service import AuthService

app = FastAPI()

app.include_router(auth_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str, access_token: Annotated[AccessToken, Depends(AuthService.get_current_active_user)]):
    return {"message": f"Hello {name}"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
