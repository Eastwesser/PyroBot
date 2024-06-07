import logging
import unittest
from unittest.mock import MagicMock, patch

from main import handle_message

# Configure logging to capture log messages during tests
logging.basicConfig(level=logging.INFO)


class TestBot(unittest.TestCase):
    @patch('main.session')
    def test_handle_message_keyword_present_finish(self, mock_session):
        # Mock the Pyrogram message object with "прекрасно"
        message = MagicMock()
        message.text.lower.return_value = "прекрасно"
        message.from_user.id = 123  # Sample user ID

        # Call the handle_message function with the mocked message
        handle_message(None, message)

        # Check if the user's status is updated to 'finished'
        mock_session.query.return_value.filter_by.return_value.first.assert_called_once_with()
        mock_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        mock_session.commit.assert_called_once()

    @patch('main.session')
    def test_handle_message_keyword_present_wait(self, mock_session):
        # Mock the Pyrogram message object with "ожидать"
        message = MagicMock()
        message.text.lower.return_value = "ожидать"
        message.from_user.id = 456  # Sample user ID

        # Call the handle_message function with the mocked message
        handle_message(None, message)

        # Check if the user's status is updated to 'finished'
        mock_session.query.return_value.filter_by.return_value.first.assert_called_once_with()
        mock_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        mock_session.commit.assert_called_once()

    @patch('main.session')
    def test_handle_message_keyword_not_present(self, mock_session):
        # Mock the Pyrogram message object
        message = MagicMock()
        message.text.lower.return_value = "hello"
        message.from_user.id = 456  # Sample user ID

        # Call the handle_message function with the mocked message
        handle_message(None, message)

        # Check if the user's status is not updated
        mock_session.query.return_value.filter_by.return_value.first.assert_not_called()
        mock_session.commit.assert_not_called()


if __name__ == '__main__':
    unittest.main()
