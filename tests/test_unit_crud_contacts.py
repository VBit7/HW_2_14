import unittest
from datetime import date
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User, Contact
from src.contacts.schemas import ContactSchema, ContactResponse
from src.contacts.crud import get_contacts, get_contact, create_contact, update_contact, delete_contact


# create_todo, get_all_todos, get_todo, update_todo, delete_todo, get_todos


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password="password", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone_number='1234567890',
                date_of_birth=date(1990, 5, 20),
                additional_data='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
                created_at=date.today(),
                updated_at=date.today(),
                user_id=self.user.id,
                user=self.user
            ),
            Contact(
                id=2,
                first_name='Jane',
                last_name='Smith',
                email='jane.smith@example.com',
                phone_number='9876543210',
                date_of_birth=date(1985, 8, 15),
                additional_data='Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
                created_at=date.today(),
                updated_at=date.today(),
                user_id=self.user.id,
                user=self.user
            )
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 1
        contact = [
            Contact(
                id=1,
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone_number='1234567890',
                date_of_birth=date(1990, 5, 20),
                additional_data='Lorem ipsum dolor sit amet, consectetur adipiscing elit.',
                created_at=date.today(),
                updated_at=date.today(),
                user_id=self.user.id,
                user=self.user
            )
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contacts
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = ContactSchema(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='1234567890',
            date_of_birth=date(1990, 5, 20),
            additional_data='Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        )
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.date_of_birth, body.date_of_birth)
        self.assertEqual(result.additional_data, body.additional_data)

    async def test_update_contact(self):
        contact_id = 1
        body = ContactSchema(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='1234567890',
            date_of_birth=date(1990, 5, 20),
            additional_data='Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
        )
        contact = Contact(
            id=contact_id,
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone_number='9876543210',
            date_of_birth=date(1985, 8, 15),
            additional_data='Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
        )

        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await update_contact(contact_id, body, self.session, self.user)

        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.date_of_birth, body.date_of_birth)
        self.assertEqual(result.additional_data, body.additional_data)
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(contact)


    async def test_delete_contact(self):
        contact_id = 1
        contact = Contact(
            id=contact_id,
            first_name='Jane',
            last_name='Smith',
            email='jane.smith@example.com',
            phone_number='9876543210',
            date_of_birth=date(1985, 8, 15),
            additional_data='Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
        )
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()

        self.assertIsInstance(result, Contact)


if __name__ == '__main__':
    unittest.main()
