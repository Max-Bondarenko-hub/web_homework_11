import unittest
from unittest.mock import AsyncMock

from sqlalchemy.orm.session import Session

from src.repository import accounts
from src.database.models import Account
from src.schemas import AccountModel


class TestAccounts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_session = AsyncMock(spec=Session)

    async def test_get_user_by_email(self):
        user_email = 'test@gmail.com'
        user = Account(email=user_email)
        self.mock_session.query().filter().first.return_value = user
        result = await accounts.get_user_by_email(user_email, self.mock_session)
        self.assertEqual(result, user)

    async def test_get_email_by_username(self):
        username = 'test_user'
        user = Account(login=username)
        self.mock_session.query().filter().first.return_value = user
        result = await accounts.get_email_by_username(username, self.mock_session)
        self.assertEqual(result, user)

    async def test_create_account(self):
        account_data = AccountModel(login='test_user', email='test@gmail.com', password='password')
        user = Account(**account_data.dict())
        self.mock_session.add.return_value = None
        self.mock_session.commit.return_value = None
        self.mock_session.refresh.return_value = None
        result = await accounts.create_account(account_data, self.mock_session)
        self.assertEqual(result.login, account_data.login)
        self.assertEqual(result.email, account_data.email)

    async def test_update_token(self):
        user = Account()
        token = "test_token"
        await accounts.update_token(user, token, self.mock_session)
        self.assertEqual(user.refresh_token, token)
        self.mock_session.commit.assert_called_once()

    async def test_confirmed_email(self):
        user_email = 'test@gmail.com'
        user = Account(email=user_email)
        self.mock_session.query().filter().first.return_value = user
        await accounts.confirmed_email(user_email, self.mock_session)
        self.assertTrue(user.confirmed)
        self.mock_session.commit.assert_called_once()

    async def test_update_avatar(self):
        user_email = 'test@gmail.com'
        user = Account(email=user_email)
        new_avatar_url = 'http://test.com/avatar.png'
        self.mock_session.query().filter().first.return_value = user
        result = await accounts.update_avatar(user_email, new_avatar_url, self.mock_session)
        self.assertEqual(result, user)
        self.assertEqual(user.avatar, new_avatar_url)
        self.mock_session.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()