import contextlib

import sqlalchemy.ext.asyncio as asyncio

from src.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: asyncio.AsyncEngine | None = asyncio.create_async_engine(url)
        self._session_maker: asyncio.async_sessionmaker = asyncio.async_sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    async with sessionmanager.session() as session:
        yield session
