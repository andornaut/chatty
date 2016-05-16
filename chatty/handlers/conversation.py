from chatty import ORIBTED_STATIC_PORT, ENCRYPTION_COOKIE_NAME
from chatty.authentication import logout_and_purge_cookies
from chatty.commands import ResponseHelper, command_factory
from chatty.handlers import Handler, _strip, \
    _get_authenticated_or_anonymous_avatar, _flash
from chatty.models import Conversation, Message
from chatty.utils import create_conversation_dict, create_messages_dict
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.url import route_url
from pyramid_handlers import action
from sqlalchemy.orm.exc import NoResultFound


class ConversationHandler(Handler):
    @action(renderer='json', xhr=True)
    def post(self):
        Response()
        request = self.request
        title = _strip(request.matchdict['title'])
        command = _strip(request.POST.get('command'))
        body = _strip(request.POST.getone('body'))
        is_encrypted = bool(request.POST.get('is_encrypted'))
        avatar = _get_authenticated_or_anonymous_avatar(request)
        if not avatar:
            url_view = route_url('conversations-view', request, title=title)
            error = 'Your session timed out. Please set a nickname or <a href="/p/login" class="login" title="Login / Register">Login / Register</a>.'
            _flash(request, error)
            logout_and_purge_cookies(request)
            return ResponseHelper.redirect(url_view)
        try:
            conversation = Conversation.with_title(title)
        except NoResultFound:
            return ResponseHelper.conversation_ended()
        command = command_factory(command, body)
        return command.execute(request=request,
                               conversation=conversation,
                               avatar=avatar,
                               is_encrypted=is_encrypted)

    @action(renderer='conversation.mak')
    def view(self):
        request = self.request
        title = request.matchdict['title']
        try:
            conversation = Conversation.with_title(title)
        except NoResultFound:
            _flash(request, 'Sorry, that conversation doesn\'t  exist')
            url_home = route_url('home', request)
            return HTTPFound(location=url_home)
        url_orbited = request.host_url
        pos = url_orbited.rfind(':')
        if pos > 5:
            url_orbited = url_orbited[0:pos]
        url_orbited += ':%s' % ORIBTED_STATIC_PORT
        url_view = route_url('conversations-view', request, title=title)
        context = {'conversation': create_conversation_dict(conversation),
                   'cookie_name': ENCRYPTION_COOKIE_NAME,
                   'url_orbited': url_orbited,
                   'url_view': url_view }
        avatar = _get_authenticated_or_anonymous_avatar(request)
        if avatar:
            context['private_key'] = avatar.private_key
        return context

    @action(renderer="json", xhr=True)
    def view_latest(self):
        request = self.request
        conversation_title = request.matchdict['title']
        try:
            conversation = Conversation.with_title(conversation_title)
        except NoResultFound:
            return ResponseHelper.conversation_ended()
        messages = Message.with_conversation(conversation.id)
        return {'messages':create_messages_dict(messages)}

    @action(renderer="json", xhr=True)
    def view_before_message(self):
        request = self.request
        conversation_title = request.matchdict['title']
        message_id = request.matchdict['message_id']
        try:
            conversation = Conversation.with_title(conversation_title)
        except NoResultFound:
            return ResponseHelper.conversation_ended()
        messages = Message.with_conversation_before_message(conversation.id, message_id)
        return {'messages':create_messages_dict(messages)}