import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from pyrogram import Client
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, User

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
db_url = os.getenv('DB_URL')

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the Telegram client
app = Client(
    'my_bot',
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# Initialize the database engine
engine = create_engine(db_url)

# Create database tables
Base.metadata.create_all(engine)

# Configure session
Session = sessionmaker(bind=engine)
session = Session()


@app.on_message()
def handle_message(client, message):
    try:
        text = message.text.lower()
        user_id = str(message.from_user.id)  # Use the actual user ID from Telegram

        # Fetch or create the user
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            user = User(id=user_id)
            session.add(user)
            session.commit()

        if "прекрасно" in text:
            user.status = 'finished'
            user.status_updated_at = datetime.utcnow()
            session.commit()
            logger.info(f"User {user_id} status updated to 'finished'")

            sent_message = client.send_message(user_id, "Ваша воронка успешно завершена!")
            if sent_message:
                logger.info(f"Sent message to user {user_id}")
            return

        if "ожидать" in text:
            user.status = 'waiting'
            user.status_updated_at = datetime.utcnow()
            session.commit()
            logger.info(f"User {user_id} status updated to 'waiting'")

            sent_message = client.send_message(
                user_id, "Вы находитесь в состоянии ожидания. Мы свяжемся с вами в ближайшее время."
            )
            if sent_message:
                logger.info(f"Sent message to user {user_id}")
            return

        logger.info(f"Received message from user {user_id}: {text}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == '__main__':
    try:
        logger.info("Starting the bot")
        app.run()
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")
