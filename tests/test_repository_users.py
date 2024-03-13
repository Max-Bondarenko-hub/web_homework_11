import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from src.database.models import User, Account
from src.schemas import UserModel, UserUpdate
from src.repository.users import (
    get_users,
    get_user,
    find_user,
    upcoming_birthdays,
    create_user,
    remove_user,
    update_user,
)


class TestUserRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.current_user = Account(id=1)
        self.user_model = UserModel(
            name="U_Test",
            surname="Sur_Test",
            email="u_test.sur_test@gmail.com",
            phone="123456789",
            birthdate=datetime.now().date(),
            additional_data="Info",
        )
        self.user_update = UserUpdate(
            name="New Name",
            surname="New Surname",
            email="new.email@gmail.com",
            phone="987654321",
            birthdate=datetime.now().date() - timedelta(days=365 * 30),
            additional_data="New info",
        )

    async def test_get_users(self):
        self.mock_session.query().filter().offset().limit().all.return_value = [User(), User(), User()]
        result = await get_users(skip=0, limit=10, account=self.current_user, db=self.mock_session)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], User)

    async def test_get_user(self):
        self.mock_session.query().filter().first.return_value = User(id=1, name="U_Test", email="U_Test@gmail.com")
        result = await get_user(user_id=1, account=self.current_user, db=self.mock_session)
        self.assertIsInstance(result, User)

    async def test_find_user(self):
        expected_user = User(id=1, name="U_Test", email="U_Test@gmail.com")
        self.mock_session.query().filter().filter().filter().first.return_value = expected_user
        result = await find_user(
            user_name="U_Test", user_surname="Doe", user_email="U_Test@gmail.com", account=self.current_user, db=self.mock_session
        )
        self.assertEqual(result, expected_user)

    async def test_upcoming_birthdays(self):
        self.mock_session.query().filter().all.return_value = [User(), User(), User()]
        result = await upcoming_birthdays(db=self.mock_session, account=self.current_user, days=7)
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0], User)

    async def test_create_user(self):
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        result = await create_user(body=self.user_model, current_user=self.current_user, db=self.mock_session)
        self.assertIsInstance(result, User)

    async def test_remove_user(self):
        self.mock_session.query().filter().first.return_value = User(id=1, name="U_Test", email="U_Test@gmail.com")
        self.mock_session.delete.return_value = None
        self.mock_session.commit.return_value = None
        result = await remove_user(user_id=1, account=self.current_user, db=self.mock_session)
        self.assertIsInstance(result, User)

    async def test_update_user(self):
        self.mock_session.query().filter().first.return_value = User(id=1, name="U_Test", email="U_Test@gmail.com")
        self.mock_session.commit.return_value = None
        result = await update_user(user_id=1, body=self.user_update, account=self.current_user, db=self.mock_session)
        self.assertIsInstance(result, User)


if __name__ == "__main__":
    unittest.main()