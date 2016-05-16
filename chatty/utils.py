from time import mktime
import datetime
import logging

log = logging.getLogger(__name__)

STATUS_ERROR = 'ERROR'
STATUS_FRIEND = 'FRIEND'
STATUS_MESSAGE = 'MESSAGE'
STATUS_NICKNAME = 'NICKNAME'
STATUS_OK = 'OK'
STATUS_REDIRECT = 'REDIRECT'
DATETIME_FORMAT = 'N j, Y H:i:s T'

def create_friend_dict(friends):
    return [{'nickname': friend.nickname, 'is_online': friend.is_online}
            for friend in friends]

def create_message_dict(message):
    if hasattr(message, 'id'):
        id = message.id,
        body = message.body
        nickname = message.nickname
        is_encrypted = message.is_encrypted
        is_private = False
    else:
        id = message.get('id')
        body = message.get('body')
        nickname = message.get('nickname')
        is_encrypted = message.get('is_encrypted')
        is_private = True
    return {'status': STATUS_MESSAGE,
            'id': id,
            'body': body,
            'nickname':nickname,
            'is_encrypted': is_encrypted,
            'is_private': is_private}

def create_messages_dict(messages):
    if messages.count():
        messages = messages.all()
        messages.reverse()
        return [create_message_dict(message) for message in messages]
    return []

def create_conversation_dict(conversation):
    return {'created': format_date(conversation.created),
            'created_by': conversation.nickname,
            'is_anonymous': conversation.is_anonymous,
            'title': conversation.title,
            'topic': conversation.topic,
            'topic_changed': format_date(conversation.topic_changed),
            'topic_changed_by': conversation.topic_changed_nickname}

def create_conversations_dict(conversations):
    if conversations.count():
        return [create_conversation_dict(message) for message in conversations]
    return []

def now():
    return datetime.datetime.now()

def str_timestamp():
    return str(mktime(now().timetuple())).replace('.', '')

def format_date(dt):
    if not dt:
        return ''
    l = dt.strftime('%B %d, %Y at ')
    r = dt.strftime('%I:%M%p').lstrip('0').lower()
    return l + r
