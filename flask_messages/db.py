from sqlalchemy import create_engine, Column, Integer, String
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

    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'message': self.message}


def post_message(user_id, message):
    s = Session()
    m = Message()
    m.user_id = user_id
    m.message = message
    s.add(m)
    s.commit()
    s.close()
    return m


def search_messages(search):
    s = Session()
    messages_query = s.query(Message).filter(Message.message.ilike('%{}%'.format(search)))
    # in real life, don't allow wildcard search injection like this
    messages = list(messages_query)
    s.close()
    return messages
