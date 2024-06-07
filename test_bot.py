import unittest
import uuid
from unittest.mock import MagicMock, patch

from main import handle_message, session, app, User, logger


class TestBot(unittest.TestCase):
    def setUp(self):
        self.user_id = str(uuid.uuid4())  # Generate a unique user ID for each test

    @patch('main.Client.send_message')
    def test_handle_message_keyword_present_finish(self, mock_send_message):
        user_id = self.user_id
        message = MagicMock()
        message.text.lower.return_value = "прекрасно"
        message.from_user.id = user_id

        user = User(id=user_id)
        session.add(user)
        session.commit()

        handle_message(app, message)

        updated_user = session.query(User).filter_by(id=user_id).first()
        self.assertEqual(updated_user.status, 'finished')
        mock_send_message.assert_called_once_with(
            user_id, "Ваша воронка успешно завершена!"
        )

    @patch('main.Client.send_message')
    def test_handle_message_keyword_present_wait(self, mock_send_message):
        user_id = self.user_id
        message = MagicMock()
        message.text.lower.return_value = "ожидать"
        message.from_user.id = user_id

        user = User(id=user_id)
        session.add(user)
        session.commit()

        handle_message(app, message)

        updated_user = session.query(User).filter_by(id=user_id).first()
        self.assertEqual(updated_user.status, 'waiting')
        mock_send_message.assert_called_once_with(
            user_id, "Вы находитесь в состоянии ожидания. Мы свяжемся с вами в ближайшее время."
        )

    @patch('main.Client.send_message')
    def test_handle_message_keyword_not_present(self, mock_send_message):
        user_id = self.user_id
        message = MagicMock()
        message.text.lower.return_value = "random text"
        message.from_user.id = user_id

        handle_message(app, message)

        mock_send_message.assert_not_called()

    @patch('main.Client.send_message')
    def test_handle_message_exception(self, mock_send_message):
        user_id = self.user_id
        message = MagicMock()
        message.text.lower.return_value = "прекрасно"
        message.from_user.id = user_id

        session.query = MagicMock(side_effect=Exception("Test Exception"))

        handle_message(app, message)

        mock_send_message.assert_not_called()
        self.assertTrue(logger.error.called)


if __name__ == '__main__':
    unittest.main()
