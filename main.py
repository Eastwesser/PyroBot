import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from pyrogram import Client
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
db_url = os.getenv('DB_URL')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Client(
    'my_bot',
    api_id=api_id,
    api_hash=api_hash,
    bot_token=bot_token
)

engine = create_engine(db_url)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='alive')
    status_updated_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


@app.on_message()
def handle_message(client, message):
    text = message.text.lower()
    user_id = message.from_user.id

    if "прекрасно" in text or "ожидать" in text:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.status = 'finished'
            user.status_updated_at = datetime.utcnow()
            session.commit()
            logger.info(f"User {user_id} status updated to 'finished'")
        return

    logger.info(f"Received message from user {user_id}: {text}")


if __name__ == '__main__':
    logger.info("Starting the bot")
    app.run()
