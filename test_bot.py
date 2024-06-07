import unittest
from datetime import datetime
from unittest.mock import patch, AsyncMock

from pyrogram import Client

from main import (
    get_or_create_user,
    update_user_status,
    handle_message,
)
from models import User


class TestMain(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user_id = "12345"
        self.mock_client = AsyncMock(spec=Client)
        self.mock_message = AsyncMock()
        self.mock_message.text = "test message"
        self.mock_message.from_user.id = self.user_id

    async def test_get_or_create_user(self):
        with patch("main.SessionLocal") as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value = None
            user = await get_or_create_user(self.user_id)
            self.assertIsInstance(user, User)
            self.assertEqual(user.id, self.user_id)

            mock_session.return_value.__aenter__.return_value.get.return_value = User(id=self.user_id)
            user = await get_or_create_user(self.user_id)
            self.assertIsInstance(user, User)
            self.assertEqual(user.id, self.user_id)

    async def test_update_user_status(self):
        with patch("main.SessionLocal") as mock_session:
            mock_session.return_value.__aenter__.return_value.get.return_value = None
            result = await update_user_status(self.user_id, "finished")
            self.assertFalse(result)

            mock_user = User(id=self.user_id)
            mock_session.return_value.__aenter__.return_value.get.return_value = mock_user
            result = await update_user_status(self.user_id, "waiting")
            self.assertTrue(result)
            self.assertEqual(mock_user.status, "waiting")
            self.assertIsInstance(mock_user.status_updated_at, datetime)

    async def test_handle_message_prekrasno(self):
        with patch("main.get_or_create_user") as mock_get_or_create_user, \
                patch("main.update_user_status") as mock_update_user_status:
            mock_get_or_create_user.return_value = User(id=self.user_id)
            mock_update_user_status.return_value = True
            self.mock_message.text = "прекрасно"

            await handle_message(self.mock_client, self.mock_message)

            mock_get_or_create_user.assert_awaited_once()
            mock_update_user_status.assert_awaited_once_with(self.user_id, "finished")
            self.mock_client.send_message.assert_called_once_with(self.user_id, "Ваша воронка успешно завершена!")

    async def test_handle_message_ozhidat(self):
        with patch("main.get_or_create_user") as mock_get_or_create_user, \
                patch("main.update_user_status") as mock_update_user_status:
            mock_get_or_create_user.return_value = User(id=self.user_id)
            mock_update_user_status.return_value = True
            self.mock_message.text = "ожидать"

            await handle_message(self.mock_client, self.mock_message)

            mock_get_or_create_user.assert_awaited_once()
            mock_update_user_status.assert_awaited_once_with(self.user_id, "waiting")
            self.mock_client.send_message.assert_called_once_with(
                self.user_id, "Вы находитесь в состоянии ожидания. Мы свяжемся с вами в ближайшее время."
            )


if __name__ == '__main__':
    unittest.main()
