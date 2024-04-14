import fastapi
import src.db as db

import sqlalchemy.ext.asyncio as asyncio

import src.auth.models as models
import src.contacts.schemas as contacts_schemas
import src.contacts.crud as contacts_crud
from src.auth.services import auth_service

from fastapi_limiter.depends import RateLimiter

router = fastapi.APIRouter(prefix='/contacts', tags=["contacts"])


@router.get(
    "/",
    response_model=list[contacts_schemas.ContactResponse],
    description='No more than 10 requests per minute',
    dependencies=[fastapi.Depends(RateLimiter(times=10, seconds=60))]
)
async def get_contacts(
        limit: int = fastapi.Query(10, ge=10, le=500),
        offset: int = fastapi.Query(0, ge=0),
        db: asyncio.AsyncSession = fastapi.Depends(db.get_db),
        user: models.User = fastapi.Depends(auth_service.get_current_user),
):
    """
    The get_contacts function returns a list of contacts for the current user.

    :param limit: int: Limit the number of contacts returned
    :param ge: Set a minimum value for the limit parameter
    :param le: Specify the maximum value that can be passed to the limit parameter
    :param offset: int: Skip the first offset number of contacts
    :param ge: Specify that the limit must be greater than or equal to 10
    :param db: asyncio.AsyncSession: Get the database session
    :param user: models.User: Get the current user from the database

    :return: A list of contacts
    """
    contacts = await contacts_crud.get_contacts(limit, offset, db, user)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=contacts_schemas.ContactResponse,
    description='No more than 10 requests per minute',
    dependencies=[fastapi.Depends(RateLimiter(times=10, seconds=60))]
)
async def get_contact(
        contact_id: int = fastapi.Path(ge=1),
        db: asyncio.AsyncSession = fastapi.Depends(db.get_db),
        user: models.User = fastapi.Depends(auth_service.get_current_user),
):
    """
    The get_contact function returns a contact by its id.

    :param contact_id: int: Specify the path parameter, which is used to get a specific contact
    :param db: asyncio.AsyncSession: Get the database connection
    :param user: models.User: Get the current user

    :return: A contact object
    """
    contact = await contacts_crud.get_contact(contact_id, db, user)
    if contact is None:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.post(
    "/", response_model=contacts_schemas.ContactResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
    description='No more than 5 requests per minute',
    dependencies=[fastapi.Depends(RateLimiter(times=5, seconds=60))]
)
async def create_contact(
        body: contacts_schemas.ContactSchema,
        db: asyncio.AsyncSession = fastapi.Depends(db.get_db),
        user: models.User = fastapi.Depends(auth_service.get_current_user),
):
    """
    The create_contact function creates a new contact in the database.

    :param body: contacts_schemas.ContactSchema: Validate the request body
    :param db: asyncio.AsyncSession: Get the database session
    :param user: models.User: Get the current user

    :return: The contact that was just created
    """
    contact = await contacts_crud.create_contact(body, db, user)
    return contact


@router.put("/{contact_id}")
async def update_contact(
        body: contacts_schemas.ContactSchema,
        contact_id: int = fastapi.Path(ge=1),
        db: asyncio.AsyncSession = fastapi.Depends(db.get_db),
        user: models.User = fastapi.Depends(auth_service.get_current_user),
):
    """
    The update_contact function updates a contact in the database.

    :param body: contacts_schemas.ContactSchema: Get the data from the request body
    :param contact_id: int: Get the contact id from the url path
    :param db: asyncio.AsyncSession: Get the database session
    :param user: models.User: Get the current user from the database

    :return: A contact object
    """
    contact = await contacts_crud.update_contact(contact_id, body, db, user)
    if contact is None:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete(
    "/{contact_id}",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    description='No more than 5 requests per minute',
    dependencies=[fastapi.Depends(RateLimiter(times=5, seconds=60))]
)
async def delete_contact(
        contact_id: int = fastapi.Path(ge=1),
        db: asyncio.AsyncSession = fastapi.Depends(db.get_db),
        user: models.User = fastapi.Depends(auth_service.get_current_user),
):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact id
    :param db: asyncio.AsyncSession: Get the database session
    :param user: models.User: Get the current user from the database

    :return: A contact object, which is the same as
    """
    contact = await contacts_crud.delete_contact(contact_id, db, user)
    return contact


@router.get(
    "/search/{query}",
    response_model=list[contacts_schemas.ContactResponse],
    description='No more than 10 requests per minute',
    dependencies=[fastapi.Depends(RateLimiter(times=10, seconds=60))]
)
async def search_contacts(
        query: str,
        db: asyncio.AsyncSession = fastapi.Depends(db.get_db),
        user: models.User = fastapi.Depends(auth_service.get_current_user),
):
    """
    The search_contacts function searches for contacts in the database.
        It takes a query string and returns a list of contacts that match the query.
        The user must be logged in to use this function.

    :param query: str: Search for contacts with a specific name
    :param db: asyncio.AsyncSession: Get a database connection
    :param user: models.User: Get the current user from the database

    :return: A list of contacts
    """
    contacts = await contacts_crud.search_contacts(query, db, user)
    if contacts is None:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.get(
    "/upcoming_birthdays/",
    response_model=list[contacts_schemas.ContactResponse],
    description='No more than 10 requests per minute',
    dependencies=[fastapi.Depends(RateLimiter(times=10, seconds=60))]
)
async def upcoming_birthdays(
        db: asyncio.AsyncSession = fastapi.Depends(db.get_db),
        user: models.User = fastapi.Depends(auth_service.get_current_user),
):
    """
    The upcoming_birthdays function returns a list of contacts that have birthdays in the next 7 days.

    :param db: asyncio.AsyncSession: Get the database session
    :param user: models.User: Get the current user

    :return: A list of contacts that have a birthday in the next 7 days
    """
    contacts = await contacts_crud.congratulate(db, user)
    if contacts is None:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts
