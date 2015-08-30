import bcrypt
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

engine = create_engine('sqlite:///userdb.sqlite3')
Base = declarative_base()
Session = sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String(length=60))


def create_user(username, password):
    # no validation, or anything like that. for simplicity in this example, we consider the happy case only
    s = Session()
    u = User()
    u.username = username
    u.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    s.add(u)
    s.commit()  # will throw error if username exists, in real life you would catch this to prevent 500s in HTTP layer
    s.close()


def authenticate_user(username, password):
    s = Session()
    try:
        u = s.query(User).filter_by(username=username).one()
    except (NoResultFound, MultipleResultsFound):
        return None
    finally:
        s.close()

    if bcrypt.hashpw(password.encode('utf-8'), u.password_hash.encode('utf-8')) == u.password_hash:
        return u

    return None


def get_user_by_id(user_id):
    s = Session()
    try:
        u = s.query(User).filter_by(id=user_id).one()
    except (NoResultFound, MultipleResultsFound):
        return None
    finally:
        s.close()

    return u


def process_request_message(message):
    response = None

    if message['action'] == 'signup':
        create_user(message['username'], message['password'])
        response = {'success': True}
    elif message['action'] == 'login':
        u = authenticate_user(message['username'], message['password'])

        if u:
            response = {'username': u.username, 'id': u.id}
        else:
            response = {'id': None}
    elif message['action'] == 'get_user':
        u = get_user_by_id(message['user_id'])
        if u:
            response = {'id': u.id, 'username': u.username}
        else:
            response = {'id': None}

    return response
