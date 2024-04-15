import unittest
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema
from src.repository.contacts import create_contact, get_all_contacts, get_contact, update_contact, delete_contact, \
    get_contacts


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password="qwerty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        # Створюємо фіктивні контакти з заданими значеннями полів
        contacts = [
            Contact(
                id=1,
                first_name='test_first_name_1',
                last_name='test_last_name_1',
                email='test_email_1@example.com',
                phone_number='1234567890',
                birthday='2000-01-01',
                extra_info='Some extra info',
                completed=True,
                created_at='2024-03-22T12:00:00',
                updated_at='2024-03-22T12:00:00',
                user=self.user
            ),
            Contact(
                id=2,
                first_name='test_first_name_2',
                last_name='test_last_name_2',
                email='test_email_2@example.com',
                phone_number='0987654321',
                birthday='2001-01-01',
                extra_info='Some other info',
                completed=False,
                created_at='2024-03-22T12:00:00',
                updated_at='2024-03-22T12:00:00',
                user=self.user
            )
        ]
        # Створюємо фіктивний результат запиту до бази даних
        mocked_result = MagicMock()
        mocked_result.scalars.return_value.all.return_value = contacts
        # Моделюємо поведінку сесії бази даних
        self.session.execute.return_value = mocked_result
        # Викликаємо тестовану функцію
        result = await get_all_contacts(limit, offset, self.session)
        # Перевіряємо, чи отримані контакти мають очікувані значення полів
        self.assertEqual(result[0].id, 1)
        self.assertEqual(result[0].first_name, 'test_first_name_1')
        self.assertEqual(result[0].last_name, 'test_last_name_1')
        self.assertEqual(result[0].email, 'test_email_1@example.com')
        self.assertEqual(result[0].phone_number, '1234567890')
        self.assertEqual(result[0].birthday, '2000-01-01')
        self.assertEqual(result[0].extra_info, 'Some extra info')
        self.assertTrue(result[0].completed)
        self.assertEqual(result[0].created_at, '2024-03-22T12:00:00')
        self.assertEqual(result[0].updated_at, '2024-03-22T12:00:00')
        self.assertEqual(result[0].user, self.user)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(
                id=1,
                first_name='test_first_name_1',
                last_name='test_last_name_1',
                email='test_email_1@example.com',
                phone_number='1234567890',
                birthday='2000-01-01',
                extra_info='Some extra info',
                completed=True,
                created_at='2024-03-22T12:00:00',
                updated_at='2024-03-22T12:00:00',
                user=self.user
            ),
            Contact(
                id=2,
                first_name='test_first_name_2',
                last_name='test_last_name_2',
                email='test_email_2@example.com',
                phone_number='0987654321',
                birthday='2001-01-01',
                extra_info='Some other info',
                completed=False,
                created_at='2024-03-22T12:00:00',
                updated_at='2024-03-22T12:00:00',
                user=self.user
            )
        ]
        mocked_contacts = Mock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        # Створюємо фіктивний об'єкт контакту
        body = ContactSchema(
                first_name='test_first_name_2',
                last_name='test_last_name_2',
                email='test_email_2@example.com',
                phone_number='0987654321',
                birthday='2001-01-01',
                extra_info='Some other info',
                completed=False,
                created_at='2024-03-22T12:00:00',
                updated_at='2024-03-22T12:00:00',
                user=self.user
            )
        # Викликаємо функцію створення контакту
        result = await create_contact(body, self.session, self.user)
        # Перевіряємо, чи результат є екземпляром класу Contact
        self.assertIsInstance(result, Contact)
        # Перевіряємо, чи поля контакту мають очікувані значення
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.extra_info, body.extra_info)
        self.assertEqual(result.completed, body.completed)

    async def test_update_contact(self):
        # Підготовка вхідних даних
        contact_id = 1
        body = ContactUpdateSchema(
            first_name='test_first_name_2',
            last_name='test_last_name_2',
            email='test_email_2@example.com',
            phone_number='0987654321',
            birthday='2001-01-01',
            extra_info='Some other info',
            completed=False
        )
        # Підготовка макету результату запиту до бази даних
        mocked_contact = Contact(
            id=contact_id,
            first_name='old_first_name',
            last_name='old_last_name',
            email='old_email@example.com',
            phone_number='9876543210',
            birthday='1990-01-01',
            extra_info='Old extra info'
        )
        # Макет результату запиту до бази даних
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = mocked_contact
        self.session.execute.return_value = mocked_result

        # Виклик функції update_contact
        result = await update_contact(contact_id, body, self.session, self.user)

        # Перевірка, чи оновлено контакт з вірними даними
        self.assertEqual(result.id, contact_id)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertEqual(result.birthday, body.birthday)
        self.assertEqual(result.extra_info, body.extra_info)
        self.assertFalse(result.completed)
        # Перевірка, чи викликався метод коміту бази даних
        self.session.commit.assert_called_once()
        # Перевірка, чи викликався метод оновлення контакту в базі даних
        self.session.refresh.assert_called_once_with(mocked_contact)


    async def test_delete_contact(self):
        # Підготовка тестового контакту
        contact_id = 1
        contact = Contact(id=contact_id, first_name='Test', last_name='Contact', user=self.user)

        # Макет результату запиту до бази даних
        mocked_result = MagicMock()
        mocked_result.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_result

        # Виклик функції delete_contact
        await delete_contact(contact_id, self.session, self.user)

        # Перевірка, чи викликався метод видалення контакту з бази даних
        self.session.delete.assert_called_once_with(contact)
        # Перевірка, чи викликався метод коміту бази даних
        self.session.commit.assert_called_once()



    # async def test_delete_todo(self):
    #     mocked_todo = MagicMock()
    #     mocked_todo.scalar_one_or_none.return_value = Todo(id=1, title='test_title', description='test_description',
    #                                                        user=self.user)
    #     self.session.execute.return_value = mocked_todo
    #     result = await delete_todo(1, self.session, self.user)
    #     self.session.delete.assert_called_once()
    #     self.session.commit.assert_called_once()
    #
    #     self.assertIsInstance(result, Todo)