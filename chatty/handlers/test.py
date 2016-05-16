from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.schema import Column
from sqlalchemy.sql.functions import  current_timestamp
from sqlalchemy.types import Integer, Unicode, DateTime
import datetime

Base = declarative_base()
NICKNAME_MAX_LENGTH = 10
EMAIL_MAX_LENGTH = 10
PASSWORD_MAX_LENGTH = 10

class Foo(Base):
    __tablename__ = 'foo'

    id = Column(Integer, primary_key=True)
    nickname = Column(Unicode(NICKNAME_MAX_LENGTH), nullable=False, unique=True)
    email = Column(Unicode(EMAIL_MAX_LENGTH))
    password = Column('password', Unicode(PASSWORD_MAX_LENGTH))
    private_key = Column(Unicode(255), unique=True)


    modified = Column(DateTime, default=current_timestamp(), onupdate=current_timestamp())



if __name__ == '__main__':
    engine = create_engine('postgresql://dev:dev@localhost/chatty', echo=True)
    DBSession = scoped_session(sessionmaker(autoflush=True))
    DBSession.configure(bind=engine)
    Foo.metadata.create_all(engine)
    DBSession.flush()
    avatar = Foo(nickname=u'aaabbb',
                    email=u'a@exae.com',
                    password=u'xxxzzzz')
    DBSession.add(avatar)
    DBSession.flush()