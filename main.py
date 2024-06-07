import asyncio
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from pyrogram import Client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models import Base, User  # Importing database models

# Load environment variables from .env file
load_dotenv()

# Retrieve Telegram API credentials and database URL from environment variables
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
db_url = os.getenv('DB_URL')

# Initialize the logger instance for the main module
logger = logging.getLogger(__name__)

# Configure logging settings
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Set the logging level for SQLAlchemy to WARNING to reduce verbosity
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

# Initialize the Telegram client
app = Client(
    'my_bot',
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

# Initialize the database engine with asyncpg
async_engine = create_async_engine(db_url, echo=True, future=True)

# Configure async session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
)


# Asynchronous function to create database tables
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Asynchronous function to get or create a user in the database
async def get_or_create_user(user_id):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id)
            session.add(user)
            await session.commit()
        return user


# Asynchronous function to update user status in the database
async def update_user_status(user_id, status):
    async with SessionLocal() as session:
        user = await session.get(User, user_id)
        if user:
            user.status = status
            user.status_updated_at = datetime.utcnow()
            await session.commit()
            return True
        return False


# Event handler for incoming messages
@app.on_message()
async def handle_message(client, message):
    try:
        text = message.text.lower()  # Convert message text to lowercase
        user_id = str(message.from_user.id)  # Get user ID

        user = await get_or_create_user(user_id)  # Get or create user in the database

        # Handle messages based on their content
        if "прекрасно" in text:
            if await update_user_status(user_id, 'finished'):
                logger.info(f"User {user_id} status updated to 'finished'")
                sent_message = await client.send_message(user_id, "Ваша воронка успешно завершена!")
                if sent_message:
                    logger.info(f"Sent message to user {user_id}")

        elif "ожидать" in text:
            if await update_user_status(user_id, 'waiting'):
                logger.info(f"User {user_id} status updated to 'waiting'")
                sent_message = await client.send_message(
                    user_id, "Вы находитесь в состоянии ожидания. Мы свяжемся с вами в ближайшее время."
                )
                if sent_message:
                    logger.info(f"Sent message to user {user_id}")

        else:
            logger.info(f"Received message from user {user_id}: {text}")  # Log received message

    except Exception as e:
        logger.error(f"An error occurred: {e}")  # Log any errors that occur


# Entry point of the script
if __name__ == '__main__':
    try:
        logger.info("Starting the bot")
        asyncio.run(app.run())  # Start the Telegram client event loop
        asyncio.run(create_tables())  # Create database tables
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")  # Log any errors that occur
