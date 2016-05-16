from beaker.crypto.util import sha1
from chatty.forms import NICKNAME_MAX_LENGTH, EMAIL_MAX_LENGTH, \
    PASSWORD_MAX_LENGTH, TITLE_MAX_LENGTH, TOPIC_MAX_LENGTH, MESSAGE_MAX_LENGTH
from chatty.utils import str_timestamp, now
from cryptacular.bcrypt import BCRYPTPasswordManager #@UnresolvedImport
from pyramid.exceptions import Forbidden
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql.expression import and_, or_, desc
from sqlalchemy.sql.functions import current_timestamp
from sqlalchemy.types import Unicode, DateTime, Boolean, UnicodeText
from zope.sqlalchemy import ZopeTransactionExtension #@UnresolvedImport
import datetime
import random
import string

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Avatar(Base):
    __tablename__ = 'avatar'

    password_manager = BCRYPTPasswordManager()

    id = Column(Integer, primary_key=True)
    nickname = Column(Unicode(NICKNAME_MAX_LENGTH), nullable=False, unique=True)
    email = Column(Unicode(EMAIL_MAX_LENGTH))
    password = Column('password', Unicode(PASSWORD_MAX_LENGTH))
    private_key = Column(Unicode(255), unique=True)
    last_received_private_message_avatar_id = Column(Integer,
                                                     ForeignKey('avatar.id',
                                                                ondelete='SET NULL'))


    received_friendships = relationship('Friendship',
                                        backref='receiver_avatar',
                                        cascade='all, delete',
                                        collection_class=set,
                                        primaryjoin='Friendship.receiver_avatar_id == Avatar.id',
                                        passive_deletes=True)
    requested_friendships = relationship('Friendship',
                                         backref='requester_avatar',
                                         cascade='all, delete',
                                         collection_class=set,
                                         primaryjoin='Friendship.requester_avatar_id == Avatar.id',
                                         passive_deletes=True)
    conversations = relationship('Conversation',
                                 backref='avatar',
                                 primaryjoin='Conversation.avatar_id == Avatar.id')
    messages = relationship('Message',
                            backref='avatar',
                            cascade='all, delete',
                            passive_deletes=True,
                            primaryjoin='Message.avatar_id == Avatar.id')

    def check_password(self, raw_password):
        return self.password_manager.check(self.password, raw_password)

    @property
    def friends(self):
        received = [o.requester_avatar for o in self.received_friendships if o.is_confirmed]
        requested = [o.receiver_avatar for o in self.requested_friendships if o.is_confirmed]
        return sorted(received + requested, key=lambda o: o.nickname)

    def create_private_key(self, session_id):
        assert session_id and len(session_id) > 31
        hash = sha1()
        hash.update(session_id)
        self.private_key = hash.hexdigest() + str_timestamp()

    @property
    def is_anonymous(self):
        return not self.password

    @property
    def is_deletable(self):
        return self.accessed + datetime.timedelta(days=1) > now()

    @property
    def is_online(self):
        return self.accessed + datetime.timedelta(seconds=40) > now()

    def set_password(self, raw_password):
        self.password = self.password_manager.encode(raw_password)

    @classmethod
    def with_anonymous_id(clazz, id):
        avatar = DBSession.query(clazz).get(id)
        if avatar and avatar.password is not None:
            raise Forbidden
        return avatar

    @classmethod
    def with_id(clazz, id):
        return DBSession.query(clazz).get(id)

    @classmethod
    def with_nickname(clazz, nickname):
        q = DBSession.query(clazz).filter_by(nickname=nickname)
        return q.one()

"""
def update_messages_before_delete(mapper, connection, target):
    for m in DBSession.query(Message).filter_by(avatar_id=target.id).all():
        m.deleted_nickname = t.nickname
    
from sqlalchemy import event
event.listen(Avatar, 'before_delete', my_before_insert_listener)
"""

class Friendship(Base):
    __tablename__ = 'friendship'
    id = Column(Integer, primary_key=True)
    requester_avatar_id = Column(Integer,
                                 ForeignKey(Avatar.id, ondelete='CASCADE'))
    receiver_avatar_id = Column(Integer,
                                ForeignKey(Avatar.id, ondelete='CASCADE'))
    is_confirmed = Column(Boolean, default=False)

    @classmethod
    def with_avatars(clazz, left_avatar_id, right_avatar_id):
        clause_a = and_(clazz.requester_avatar_id == left_avatar_id,
                        clazz.receiver_avatar_id == right_avatar_id)
        clause_b = and_(clazz.requester_avatar_id == right_avatar_id,
                        clazz.receiver_avatar_id == left_avatar_id)
        return DBSession.query(clazz).filter(or_(clause_a, clause_b)).one()

class Conversation(Base):
    __tablename__ = 'conversation'
    id = Column(Integer, primary_key=True)
    avatar_id = Column(Integer, ForeignKey(Avatar.id, ondelete='SET NULL'))
    topic_avatar_id = Column(Integer, ForeignKey(Avatar.id, ondelete='SET NULL'))
    title = Column(Unicode(TITLE_MAX_LENGTH), nullable=False, unique=True)
    topic = Column(Unicode(TOPIC_MAX_LENGTH))
    expiry = Column(DateTime)
    is_anonymous = Column(Boolean, default=True)
    topic_changed = Column(DateTime, default=current_timestamp())
    created = Column(DateTime, default=current_timestamp())
    modified = Column(DateTime, default=current_timestamp(), onupdate=current_timestamp())

    topic_avatar = relationship("Avatar",
                                primaryjoin='Conversation.topic_avatar_id == Avatar.id')
    messages = relationship('Message',
                            backref='conversation',
                            cascade='all, delete',
                            order_by=desc('Message.id'),
                            passive_deletes=True)

    @staticmethod
    def create_anonymous_title(length=64):
        characters = string.letters + string.digits
        title = ''.join((random.choice(characters) for i in xrange(length - 1)))
        return title + str_timestamp()

    @classmethod
    def is_unique_title(clazz, title):
        return DBSession.query(clazz).filter_by(title=title).count() == 0

    @property
    def nickname(self):
        return (not self.is_anonymous
                and (self.avatar and self.avatar.nickname or '[deleted]')
                or '')

    @classmethod
    def latest_public(clazz, limit=20):
        q = DBSession.query(clazz).filter_by(is_anonymous=False)
        return q.order_by(desc(clazz.id)).limit(limit)

    @property
    def topic_changed_nickname(self):
        return (self.topic_avatar
                and self.topic_avatar.nickname
                or '[deleted]')

    @classmethod
    def with_title(clazz, title):
        q = DBSession.query(clazz).filter_by(title=title)
        return q.one()

class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    avatar_id = Column(Integer, ForeignKey(Avatar.id, ondelete='SET NULL'))
    conversation_id = Column(Integer,
                             ForeignKey(Conversation.id, ondelete='CASCADE'))
    body = Column(UnicodeText(MESSAGE_MAX_LENGTH))
    is_encrypted = Column(Boolean, default=False)
    #deleted_nickname = Column(Unicode(63))
    created = Column(DateTime, default=current_timestamp())
    modified = Column(DateTime, default=current_timestamp(), onupdate=current_timestamp())

    @property
    def nickname(self):
        return (self.avatar
                and self.avatar.nickname
                or '[deleted]')

    @classmethod
    def with_conversation(clazz, conversation_id, limit=50):
        q = DBSession.query(clazz).filter_by(conversation_id=conversation_id)
        return q.order_by(desc(clazz.id)).limit(limit)

    @classmethod
    def with_conversation_before_message(clazz, conversation_id, message_id, limit=50):
        q = clazz.with_conversation(conversation_id, limit)
        return q.filter_by(id < message_id)

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)

def drop_sql():
    Base.metadata.drop_all()