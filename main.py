import os

import redis.asyncio as redis
import uvicorn
from pathlib import Path

import fastapi.middleware.cors as cors
import sqlalchemy as sqa
import sqlalchemy.ext.asyncio as asyncio
from fastapi import FastAPI, Depends, HTTPException
from fastapi_limiter import FastAPILimiter

import src.db as db
from src.contacts import routes as contacts_routes
from src.auth import routes as auth_routes
from src.users import routes as users_routes
from src.config import config


app = FastAPI()

origins = ["http://localhost:8000"]

app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent

app.include_router(auth_routes.router, prefix="/api")
app.include_router(users_routes.router, prefix="/api")
app.include_router(contacts_routes.router, prefix="/api")


@app.on_event("startup")
async def startup():
    """
    The startup function is called when the application starts up.
    It's a good place to initialize things that are used by the app, such as:
    - Connecting to databases or other external services.
    - Loading configuration from files or environment variables.
    - Creating background tasks.

    :return: A list of futures, so we need to wait for them
    """
    r = await redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD
    )
    await FastAPILimiter.init(r)


@app.get('/')
def index():
    """
    The index function is a Flask view function that returns a dictionary
    containing the message 'Welcome to Contacts Application'. The index function
    is mapped to the '/' URL by default. This means that when you visit this URL,
    the index function will be called and its return value will be used as the response.

    :return: A dictionary with a message
    """
    return {'message': 'Welcome to Contacts Application'}


@app.get("/api/healthchecker")
async def healthchecker(db: asyncio.AsyncSession = Depends(db.get_db)):
    """
    The healthchecker function is a simple function that checks the health of the database.
    It does this by executing a SQL query to check if it can connect to the database and retrieve data from it.
    If there is an error connecting, or retrieving data, then we raise an HTTPException with status code 500.

    :param db: asyncio.AsyncSession: Get the database session from the dependency
    :return: A dictionary with a message
    """
    try:
        result = await db.execute(sqa.text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


if __name__ == '__main__':
    uvicorn.run(
        # 'main:app', host='localhost', port=8000, reload=True
        "main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), log_level="info"
    )
