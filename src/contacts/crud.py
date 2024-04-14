from datetime import date, timedelta
from typing import List

from sqlalchemy import select, or_, and_, extract

import sqlalchemy.ext.asyncio as asyncio

import src.auth.models as models
import src.contacts.schemas as contacts_schemas


async def get_contacts(
        limit: int,
        offset: int,
        db: asyncio.AsyncSession,
        user: models.User
) -> List[models.Contact]:
    """
    The get_contacts function returns a list of contacts for the user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the offset for pagination
    :param db: asyncio.AsyncSession: Pass a database session to the function
    :param user: models.User: Filter the contacts by user
    :return: A list of contacts
    """
    stmt = select(models.Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(
        contact_id: int,
        db: asyncio.AsyncSession,
        user: models.User
):
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: asyncio.AsyncSession: Pass the database session
    :param user: models.User: Ensure that the user is only able to access their own contacts
    :return: A contact object
    """
    stmt = select(models.Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(
        body: contacts_schemas.ContactSchema,
        db: asyncio.AsyncSession,
        user: models.User
):
    """
    The create_contact function creates a new contact in the database.

    :param body: contacts_schemas.ContactSchema: Validate the request body
    :param db: asyncio.AsyncSession: Pass in the database session
    :param user: models.User: Identify the user that is making the request
    :return: The contact object
    """
    contact = models.Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
        contact_id: int,
        body: contacts_schemas.ContactSchema,
        db: asyncio.AsyncSession,
        user: models.User
):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Specify which contact to update
    :param body: contacts_schemas.ContactSchema: Validate the request body
    :param db: asyncio.AsyncSession: Pass the database session into the function
    :param user: models.User: Ensure that the user is authorized to update the contact
    :return: A contact object
    """
    stmt = select(models.Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone_number = body.phone_number
        contact.date_of_birth = body.date_of_birth
        contact.additional_data = body.additional_data
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(
        contact_id: int,
        db: asyncio.AsyncSession,
        user: models.User
):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact to delete
    :param db: asyncio.AsyncSession: Pass the database session
    :param user: models.User: Ensure that the user is deleting their own contact
    :return: The contact that was deleted
    """
    stmt = select(models.Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(
        query: str,
        db: asyncio.AsyncSession,
        user: models.User
):
    """
    The search_contacts function searches the contacts table for a user's contacts.

    :param query: str: Filter the contacts by a string
    :param db: asyncio.AsyncSession: Pass the database session to the function
    :param user: models.User: Filter the results by user
    :return: A list of contact objects
    """
    stmt = (
        select(models.Contact)
        .filter(
            or_(
                models.Contact.first_name.ilike(f"%{query}%"),
                models.Contact.last_name.ilike(f"%{query}%"),
                models.Contact.email.ilike(f"%{query}%"),
            )
        )
        .filter_by(user=user)
    )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def congratulate(
        db: asyncio.AsyncSession,
        user: models.User
):
    """
    The congratulate function returns a list of contacts that have birthdays in the next 7 days.

    :param db: asyncio.AsyncSession: Pass the database session
    :param user: models.User: Filter the contacts by user
    :return: A list of contacts that have a birthday in the next 7 days
    """
    current_date = date.today()
    end_date = current_date + timedelta(days=7)

    stmt = (
        select(models.Contact)
        .where(
            or_(
                and_(
                    extract('month', models.Contact.date_of_birth) == current_date.month,
                    extract('day', models.Contact.date_of_birth) >= current_date.day,
                    extract('day', models.Contact.date_of_birth) <= end_date.day,
                ),
                and_(
                    extract('month', models.Contact.date_of_birth) == end_date.month,
                    extract('day', models.Contact.date_of_birth) <= end_date.day,
                ),
                and_(
                    extract('month', models.Contact.date_of_birth) == current_date.month,
                    extract('day', models.Contact.date_of_birth) == current_date.day,
                ),
            )
        )
        .filter_by(user=user)
        .order_by(extract('day', models.Contact.date_of_birth))
    )

    contacts = await db.execute(stmt)
    return contacts.scalars().all()
