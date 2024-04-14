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
        """
        The verify_password function takes a plain-text password and hashed
        password as arguments. It then uses the pwd_context object to verify that the
        plain-text password matches the hashed one.

        :param self: Make the method a bound method, which means that it can be called on instances of the class
        :param plain_password: Check the password that is entered by the user
        :param hashed_password: Compare the hashed password with the plain_password
        :return: True if the hashed password matches the plain text password
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        The get_password_hash function takes a password as input and returns the hash of that password.
        The hash is generated using the pwd_context object, which is an instance of Flask-Bcrypt's Bcrypt class.

        :param self: Represent the instance of the class
        :param password: str: Get the password from the user
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    oauth2_scheme = fastapi_security.OAuth2PasswordBearer(tokenUrl="api/auth/login")

    async def create_access_token(self, data: dict, expires_delta: typing.Optional[float] = None):
        """
        The create_access_token function creates a new access token.
            Args:
                data (dict): The data to be encoded in the JWT.
                expires_delta (Optional[float]): A timedelta object representing the time until expiration of the token.

        :param self: Refer to the current instance of a class
        :param data: dict: Pass the data that will be encoded in the jwt
        :param expires_delta: typing.Optional[float]: Set the expiration time of the token
        :return: A token that is encoded with the data, iat and exp
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, config.SECRET_KEY_JWT, algorithm=config.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: typing.Optional[float] = None):
        """
        The create_refresh_token function creates a refresh token for the user.
            Args:
                data (dict): The data to be encoded in the JWT. This should include at least a &quot;sub&quot; key, which is the subject of this token, and usually an &quot;id&quot; key with some unique identifier for that subject.
                expires_delta (Optional[float]): An optional expiration time, in seconds from now, for this token to expire in. If not provided, it will use 7 days as default value

        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded into the jwt
        :param expires_delta: typing.Optional[float]: Set the expiration time of the refresh token
        :return: A refresh token which is encoded with the jwt library
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, config.SECRET_KEY_JWT, algorithm=config.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        The decode_refresh_token function decodes the refresh token and returns the email address of the user.
        If it fails to decode, it raises an HTTPException with a 401 status code.

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass in the refresh token
        :return: The email of the user
        """
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
        """
        The get_current_user function is a dependency that returns the current user.
        It uses the OAuth2 Dependency to retrieve credentials from the Authorization header.
        If there are no credentials, or if they are invalid, it raises an HTTPException with status code 401 (Unauthorized).
        Otherwise, it gets and returns the user object from database.

        :param self: Access the class attributes
        :param token: str: Get the token from the authorization header
        :param db: asyncio.AsyncSession: Get the database session
        :return: A user object, which is the same as the one we have in our database
        """
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
        """
        The create_email_token function takes a dictionary of data and returns a JWT token.
        The token is encoded with the secret key, algorithm, and expiration date.


        :param self: Represent the instance of the class
        :param data: dict: Pass the data to be encoded in the token
        :return: A token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, config.SECRET_KEY_JWT, algorithm=config.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        The get_email_from_token function takes a token as an argument and returns the email address associated with that token.
        The function uses the jwt library to decode the token, which is then used to retrieve the email address from its payload.

        :param self: Represent the instance of the class
        :param token: str: Pass in the token that was sent to the user's email address
        :return: The email address associated with the token
        """
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
