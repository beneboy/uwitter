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
    u.password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
    s.add(u)
    s.commit()  # will throw error if username exists, in real life you would catch this to prevent 500s in HTTP layer


def authenticate_user(username, password):
    s = Session()
    try:
        u = s.query(User).filter_by(username=username).one()
    except (NoResultFound, MultipleResultsFound):
        return False

    return bcrypt.hashpw(password, u.password_hash) == u.password_hash
