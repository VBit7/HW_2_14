from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

import src.db as db
import src.auth.models as auth_models
import src.auth.schemas as auth_schemas


async def get_user_by_email(email: str, db: AsyncSession = Depends(db.get_db)):
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Specify the email of the user we want to get
    :param db: AsyncSession: Pass in the database session
    :return: A user object
    """
    stmt = select(auth_models.User).filter_by(email=email)
    user = await db.execute(stmt)
    user = user.scalar_one_or_none()
    return user


async def create_user(body: auth_schemas.UserSchema, db: AsyncSession = Depends(db.get_db)):
    """
    The create_user function creates a new user in the database.

    :param body: auth_schemas.UserSchema: Validate the request body
    :param db: AsyncSession: Get the database session
    :return: A user object
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as err:
        print(err)

    new_user = auth_models.User(**body.model_dump(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: auth_models.User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.

    :param user: auth_models.User: Specify the user that is being updated
    :param token: str | None: Specify that the token parameter can either be a string or none
    :param db: AsyncSession: Pass a database session to the function
    :return: The user object
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Specify the email address of the user to be confirmed
    :param db: AsyncSession: Pass in the database connection
    :return: None because it does not have a return statement
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()
