import asyncio
import unittest
from unittest.mock import MagicMock
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import Session

# from src.database.models import Note, Tag, User
import src.auth.models as models

# from src.schemas import NoteModel, NoteUpdate, NoteStatusUpdate
#
#
# from src.repository.notes import (
#     get_notes,
#     get_note,
#     create_note,
#     remove_note,
#     update_note,
#     update_status_note,
# )
import src.contacts.crud as contacts_repo

class TestContacts(unittest.IsolatedAsyncioTestCase):

    # def setUp(self):
    #     self.session = MagicMock(spec=Session)
    #     self.user = models.User(id=1)
    async def asyncSetUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = models.User(id=1)


    # async def test_get_contacts(self):
    #     contacts = [models.Contact(), models.Contact(), models.Contact()]
    #     self.session.query().filter().offset().limit().all.return_value = contacts
    #     result = await contacts_repo.get_contacts(limit=10, offset=0, db=self.session, user=self.user)
    #     self.assertEqual(result, contacts)
    async def test_get_contacts(self):
        contacts = [models.Contact(), models.Contact(), models.Contact()]
        # Mock the execute method to return a mock object that has a scalars method
        execute_result = AsyncMock()
        execute_result.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = execute_result

        # Call the function under test
        result = await contacts_repo.get_contacts(limit=10, offset=0, db=self.session, user=self.user)

        # Assert the result
        self.assertEqual(result, contacts)

        # Assert that the execute method was called with the correct arguments
        self.session.execute.assert_called_once()
        # You may need to add additional assertions to check the arguments passed to execute






    # async def test_get_note_found(self):
    #     note = Note()
    #     self.session.query().filter().first.return_value = note
    #     result = await get_note(note_id=1, user=self.user, db=self.session)
    #     self.assertEqual(result, note)
    #
    # async def test_get_note_not_found(self):
    #     self.session.query().filter().first.return_value = None
    #     result = await get_note(note_id=1, user=self.user, db=self.session)
    #     self.assertIsNone(result)
    #
    # async def test_create_note(self):
    #     body = NoteModel(title="test", description="test note", tags=[1, 2])
    #     tags = [Tag(id=1, user_id=1), Tag(id=2, user_id=1)]
    #     self.session.query().filter().all.return_value = tags
    #     result = await create_note(body=body, user=self.user, db=self.session)
    #     self.assertEqual(result.title, body.title)
    #     self.assertEqual(result.description, body.description)
    #     self.assertEqual(result.tags, tags)
    #     self.assertTrue(hasattr(result, "id"))
    #
    # async def test_remove_note_found(self):
    #     note = Note()
    #     self.session.query().filter().first.return_value = note
    #     result = await remove_note(note_id=1, user=self.user, db=self.session)
    #     self.assertEqual(result, note)
    #
    # async def test_remove_note_not_found(self):
    #     self.session.query().filter().first.return_value = None
    #     result = await remove_note(note_id=1, user=self.user, db=self.session)
    #     self.assertIsNone(result)
    #
    # async def test_update_note_found(self):
    #     body = NoteUpdate(title="test", description="test note", tags=[1, 2], done=True)
    #     tags = [Tag(id=1, user_id=1), Tag(id=2, user_id=1)]
    #     note = Note(tags=tags)
    #     self.session.query().filter().first.return_value = note
    #     self.session.query().filter().all.return_value = tags
    #     self.session.commit.return_value = None
    #     result = await update_note(note_id=1, body=body, user=self.user, db=self.session)
    #     self.assertEqual(result, note)
    #
    # async def test_update_note_not_found(self):
    #     body = NoteUpdate(title="test", description="test note", tags=[1, 2], done=True)
    #     self.session.query().filter().first.return_value = None
    #     self.session.commit.return_value = None
    #     result = await update_note(note_id=1, body=body, user=self.user, db=self.session)
    #     self.assertIsNone(result)
    #
    # async def test_update_status_note_found(self):
    #     body = NoteStatusUpdate(done=True)
    #     note = Note()
    #     self.session.query().filter().first.return_value = note
    #     self.session.commit.return_value = None
    #     result = await update_status_note(note_id=1, body=body, user=self.user, db=self.session)
    #     self.assertEqual(result, note)
    #
    # async def test_update_status_note_not_found(self):
    #     body = NoteStatusUpdate(done=True)
    #     self.session.query().filter().first.return_value = None
    #     self.session.commit.return_value = None
    #     result = await update_status_note(note_id=1, body=body, user=self.user, db=self.session)
    #     self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

