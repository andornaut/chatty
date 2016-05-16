from chatty.authentication import logout_and_purge_cookies
from chatty.exchanges import EXCHANGE
from chatty.forms import validate_topic, validate_message
from chatty.models import Message, DBSession, Avatar, Friendship
from chatty.utils import create_message_dict, STATUS_ERROR, STATUS_OK, \
    STATUS_REDIRECT, STATUS_FRIEND, now
from sqlalchemy.orm.exc import NoResultFound
from webhelpers.html.builder import escape
import logging

log = logging.getLogger(__name__)

class ResponseHelper(object):
    @classmethod
    def conversation_ended(clazz):
        body = 'The conversation has ended'
        return clazz.error(body)

    @classmethod
    def error(clazz, body):
        return clazz.response(body, status=STATUS_ERROR)

    @classmethod
    def errors(clazz, errors):
        errors = '. '.join(errors)
        return clazz.error(errors)

    @classmethod
    def friend(clazz, body):
        return clazz.response(body, status=STATUS_FRIEND)

    @classmethod
    def redirect(clazz, body):
        return clazz.response(body, status=STATUS_REDIRECT)

    @classmethod
    def response(clazz, body=None, status=STATUS_OK):
        context = {'status': status}
        if body is not None:
            context['body'] = body
        return context

class CommandBase(object):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    @classmethod
    def accepts(class_, name):
        return name in class_.aliases

    def error(self, error):
        body = '<strong>%s</strong> command failed: %s' % (self.name, error)
        return ResponseHelper.error(body)

    def errors(self, errors):
        body = '. '.join(errors)
        return self.error(body)

    def response(self, body=None, status=STATUS_OK):
        return ResponseHelper.response(body, status)

    def send_private_message(self, friend, message):
        name = friend.private_key
        assert name
        EXCHANGE.send_private(name, message)

    def send_public_message(self, conversation, message):
        name = conversation.title
        assert name
        EXCHANGE.send_public(name, message)

class NotFoundErrorCommand(CommandBase):
    @classmethod
    def accepts(class_, name):
        raise AssertionError()

    def execute(self, **kwargs):
        return self.error('Command not found')

class ValidationErrorCommand(CommandBase):
    @classmethod
    def accepts(class_, name):
        raise AssertionError()

    def execute(self, **kwargs):
        return self.errors(self.args)

class EndCommand(CommandBase):
    aliases = ('end', 'e', 'delete')

    def execute(self, request, avatar, conversation, **kwargs):
        if not conversation.is_anonymous and conversation.avatar and conversation.avatar != avatar:
            return self.error('Only the creator of the conversation can delete it')
        else:
            conversation_ended = ResponseHelper.conversation_ended()
            self.send_public_message(conversation, conversation_ended)
            DBSession.delete(conversation)
            return self.response()

class FriendCommandBase(CommandBase):
    def response(self, body):
        return ResponseHelper.friend(body)

    def send_private_message(self, friend, body):
        message = self.response(body)
        super(FriendCommandBase, self).send_private_message(friend, message)

class FriendAddCommand(FriendCommandBase):
    aliases = ('friendadd', 'fa')

    def execute(self, avatar, **kwargs):
        errors = []
        friend_nickname = self.args
        try:
            friend = Avatar.with_nickname(friend_nickname)
            if avatar.is_anonymous:
                errors.append('You must <a href="/p/login" class="login" title="Login / Register">login</a> in order to add friend')
            elif friend.id == avatar.id:
                errors.append('You cannot add yourself as a friend')
            elif friend.is_anonymous:
                errors.append('<strong>%s</strong> is not a registered user, and cannot receive friend requests' % friend_nickname)
            else:
                try:
                    friendship = Friendship.with_avatars(avatar.id, friend.id)
                    if friendship.is_confirmed:
                        errors.append('You are already friend with <strong>%s</strong>' % friend_nickname)
                    elif friendship.receiver_avatar_id == avatar.id:
                        friendship.is_confirmed = True
                        body = '<strong>{0}</strong> has accepted your friend request'.format(avatar.nickname)
                        self.send_private_message(friend, body)
                        body = 'You have accepted <strong>%s</strong>\'s friend request' % friend_nickname
                        return self.response(body)
                    else:
                        errors.append('You have already sent <strong>%s</strong> a friend request' % friend_nickname)
                except NoResultFound:
                    friendship = Friendship(requester_avatar_id=avatar.id, receiver_avatar_id=friend.id)
                    DBSession.add(friendship)
                    body = '<strong>{0}</strong> has sent you a friend request. <a href="#" class="chatty-send" rel="/fa {0}" title="Accept">Accept</a> | <a href="#" class="chatty-send" rel="/fr {0}" title="Reject">Reject</a>'.format(avatar.nickname)
                    self.send_private_message(friend, body)
                    body = 'You are have sent <strong>%s</strong> a friend request' % friend_nickname
                    return self.response(body)
        except NoResultFound:
            errors.append('User <strong>%s</strong> not found' % friend_nickname)
        return self.errors(errors)

class FriendRemoveCommand(FriendCommandBase):
    aliases = ('friendremove', 'fr')

    def execute(self, avatar, **kwargs):
        errors = []
        friend_nickname = self.args
        try:
            friend = Avatar.with_nickname(friend_nickname)
            if avatar.is_anonymous:
                raise AssertionError('Anonymous users shouldn\'t be have friend')
            elif friend.id == avatar.id:
                errors.append('You are not your own friend')
            else:
                try:
                    friendship = Friendship.with_avatars(avatar.id, friend.id)
                    DBSession.delete(friendship)
                    if friendship.is_confirmed:
                        body = 'You are no longer friend with <strong>%s</strong>' % friend_nickname
                    elif friendship.receiver_avatar_id == avatar.id:
                        body = 'You have rejected <strong>%s</strong>\'s friend request' % friend_nickname
                    else:
                        body = 'You have cancelled your friend request to <strong>%s</strong>' % friend_nickname
                    return self.response(body)
                except NoResultFound:
                    errors.append('You are not friend with <strong>%s</strong>' % friend_nickname)
        except NoResultFound:
            errors.append('User <strong>%s</strong> not found' % friend_nickname)
        return self.errors(errors)

class LogoutCommand(CommandBase):
    aliases = ('logout', 'l')

    def execute(self, request, avatar, **kwargs):
        logout_and_purge_cookies(request)
        return ResponseHelper.redirect('/')

class MessageCommand(CommandBase):
    def execute(self, conversation, avatar, is_encrypted, **kwargs):
        message = Message(body=self.args,
                          conversation_id=conversation.id,
                          avatar_id=avatar.id,
                          is_encrypted=is_encrypted)
        DBSession.add(message)
        DBSession.flush()
        self.send_public_message(conversation, create_message_dict(message))
        return self.response()

class PrivateMessageCommandBase(CommandBase):
    def process_private_message(self, sender, recipient, body):
        recipient.last_received_private_message_avatar_id = sender.id
        to_message = dict(body=body,
                          nickname=sender.nickname)
        self.send_private_message(recipient,
                                  create_message_dict(to_message))
        from_message = dict(body='[to %s] %s' % (recipient.nickname, body),
                            nickname=sender.nickname)
        return create_message_dict(from_message)

class ReplyCommand(PrivateMessageCommandBase):
    aliases = ('reply', 'r', 'retell')

    def execute(self, conversation, avatar, **kwargs):
        body = self.args
        errors = []
        if not body:
            errors.append('Usage: /reply &lt;to_message&gt;')
        else:
            recipient_id = avatar.last_received_private_message_avatar_id
            if not recipient_id:
                errors.append('Cannot /reply because you have not received any private messages')
            else:
                recipient = Avatar.with_id(recipient_id)
                if recipient.is_online:
                    return self.process_private_message(avatar, recipient, body)
                else:
                    errors.append('<strong>%s</strong> is offline' % recipient.nickname)
        return self.errors(errors)

class TellCommand(PrivateMessageCommandBase):
    aliases = ('msg', 'm', 'tell', 'whisper')

    def execute(self, conversation, avatar, **kwargs):
        def parse_args():
            nickname, unused, body = self.args.partition(' ')
            return nickname.strip(), body.strip()

        errors = []
        nickname, body = parse_args()
        if not body or not nickname:
            errors.append('Usage: /msg &lt;nickname&gt; &lt;body&gt;')
        else:
            try:
                recipient = Avatar.with_nickname(nickname)
                if not recipient.is_online:
                    errors.append('<strong>%s</strong> is offline' % nickname)
            except NoResultFound:
                errors.append('Unknown user: <strong>%s</strong>' % nickname)
        if not errors:
            return self.process_private_message(avatar, recipient, body)
        return self.errors(errors)

class TopicCommand(CommandBase):
    aliases = ('topic', 't')

    def execute(self, conversation, avatar, **kwargs):
        topic = self.args
        if not topic:
            if conversation.topic:
                body = 'The topic is: <strong>%s</strong>' % conversation.topic
            else:
                body = 'A topic has not been set.'
            return self.response(body)
        if not conversation.is_anonymous and conversation.avatar and conversation.avatar != avatar:
            errors = ['Only the creator of the conversation can set the topic']
        else:
            errors = validate_topic(topic)
        if errors:
            return self.errors(errors)
        else:
            topic = escape(topic)
            conversation.topic = topic
            conversation.topic_changed = now()
            conversation.topic_avatar_id = avatar.id
            body = '<strong>%s</strong> has changed the topic to <strong>%s</strong>' % (avatar.nickname, topic)
            self.send_public_message(conversation, self.response(body))
            return self.response()

COMMANDS = (EndCommand,
            FriendAddCommand,
            FriendRemoveCommand,
            LogoutCommand,
            ReplyCommand,
            TellCommand,
            TopicCommand)

def command_factory(command, body):
    body = body.strip()
    errors = validate_message(body)
    log.debug('-------------- %s' % command)
    if errors:
        return ValidationErrorCommand('send', errors)
    elif command is None:
        return MessageCommand('body', body)
    else:
        for command_class in COMMANDS:
            if command_class.accepts(command):
                return command_class(command, body)
    return NotFoundErrorCommand(command, body)