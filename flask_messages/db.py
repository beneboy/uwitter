from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///messagedb.sqlite3')
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message = Column(String(length=141))
    date_posted = Column(DateTime)

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'message': self.message}


def post_message(user_id, message):
    s = Session()
    m = Message()
    m.user_id = user_id
    m.message = message
    m.date_posted = datetime.now()
    s.add(m)
    s.commit()
    message_dict = m.to_dict()
    s.close()
    return message_dict


def search_messages(search):
    s = Session()
    messages_query = s.query(Message).filter(Message.message.ilike('%{}%'.format(search))).order_by(
        Message.date_posted.desc())
    # in real life, don't allow wildcard search injection like this
    messages = [message.to_dict() for message in messages_query]
    s.close()
    return messages


def list_messages():
    s = Session()
    messages_query = s.query(Message).order_by(Message.date_posted.desc())
    messages = [message.to_dict() for message in messages_query]
    s.close()
    return messages


def list_user_messages(user_id):
    s = Session()
    messages_query = s.query(Message).filter(Message.user_id == user_id).order_by(Message.date_posted.desc())
    messages = [message.to_dict() for message in messages_query]
    s.close()
    return messages
