import pickle
import typing
import fastapi
import passlib.context as passlib_context
import fastapi.security as fastapi_security
import redis as redis
import sqlalchemy.ext.asyncio as asyncio

from jose import jwt, JWTError
from datetime import datetime, timedelta

import src.db as db
import src.auth.crud as repository_users

from src.config import config


class Auth:
    pwd_context = passlib_context.CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    cache = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    oauth2_scheme = fastapi_security.OAuth2PasswordBearer(tokenUrl="api/auth/login")

    async def create_access_token(self, data: dict, expires_delta: typing.Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, config.SECRET_KEY_JWT, algorithm=config.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: typing.Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, config.SECRET_KEY_JWT, algorithm=config.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, config.SECRET_KEY_JWT, algorithms=[config.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail='Invalid scope for token'
            )
        except JWTError:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials'
            )

    async def get_current_user(
            self,
            token: str = fastapi.Depends(oauth2_scheme),
            db: asyncio.AsyncSession = fastapi.Depends(db.get_db)
    ):
        credentials_exception = fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, config.SECRET_KEY_JWT, algorithms=[config.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user_hash = str(email)

        user = self.cache.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, config.SECRET_KEY_JWT, algorithm=config.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, config.SECRET_KEY_JWT, algorithms=[config.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification"
            )


auth_service = Auth()
