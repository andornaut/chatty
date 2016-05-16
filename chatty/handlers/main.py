from chatty.authentication import logout_and_purge_cookies
from chatty.forms import validate_title, validate_nickname, validate_password, \
    validate_email
from chatty.handlers import Handler, _get_authenticated_avatar, \
    _get_authenticated_or_anonymous_avatar, _strip, _login, _flash, _add_error, \
    _json_redirect, _validate_nickname_uniqueness, _create_anonymous_avatar, \
    _create_avatar
from chatty.models import DBSession, Conversation
from chatty.utils import create_friend_dict, create_conversations_dict
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url
from pyramid_handlers import action
import logging

log = logging.getLogger(__name__)

WELCOME_MESSAGE = 'Welcome %s! You\'re now logged in.'


class MainHandler(Handler):
    @action(renderer='contact.mak')
    def contact(self):
        return {}

    @action(renderer='faq.mak')
    def faq(self):
        return {}

    @action(renderer='help.mak')
    def help(self):
        return {}

    @action(renderer='friends.mak', xhr=True)
    def friends(self):
        request = self.request
        avatar = _get_authenticated_avatar(request)
        if avatar:
            friends = create_friend_dict(avatar.friends)
            count = len(friends)
        else:
            friends = []
            count = 0
        return {'count': count, 'friends': friends}

    @action(renderer='home.mak')
    def home(self):
        request = self.request
        avatar = _get_authenticated_or_anonymous_avatar(request)
        errors = {}
        login_nickname, login_password, title = None, None, None
        if request.method == 'POST':
            is_anonymous = 'start_anonymous' in request.params
            if is_anonymous:
                title = Conversation.create_anonymous_title()
            else:
                title = _strip(request.POST.getone('title'))
                validate_title(title, errors)
                if not avatar or avatar.is_anonymous:
                    login_nickname = _strip(request.POST.get('login_nickname'))
                    login_password = _strip(request.POST.get('login_password'))
                    validate_nickname(login_nickname, errors, 'login_nickname')
                    validate_password(login_password, errors, 'login_password')
                    if 'login_nickname' not in errors and 'login_password' not in errors:
                        avatar = _login(request, login_nickname, login_password)
                        if avatar:
                            _flash(request, WELCOME_MESSAGE % avatar.nickname)
                        else:
                            _add_error(errors, 'login_nickname', 'Incorrect nickname or password')
            if not errors:
                if not Conversation.is_unique_title(title):
                    url_view = route_url('conversations-view', request, title=title)
                    msg = 'Conversation already exists. <a href="%s">Join in</a>!' % url_view
                    _flash(request, msg)
                else:
                    conversation = Conversation(title=title,
                                                avatar_id=avatar and avatar.id or None,
                                                is_anonymous=is_anonymous)
                    DBSession.add(conversation)
                    if avatar:
                        _flash(request, 'You can send messages by typing into the input box below and then clicking on the "send" button')
                    else:
                        _flash(request, 'Enter your nickname in the input box to the right to begin chatting')
                    url_view = route_url('conversations-view', request, title=title)
                    return HTTPFound(location=url_view)
        conversations = create_conversations_dict(Conversation.latest_public())
        return {'errors': errors,
                'conversations': conversations,
                'login_nickname': login_nickname,
                'login_password':login_password,
                'title': title, }

    @action(renderer='login.mak', xhr=True)
    def login(self):
        request = self.request
        url_from = request.GET.get('from', '/')
        if url_from == request.url:
            url_from = '/'
        avatar = _get_authenticated_avatar(request)
        if avatar:
            _flash(request, 'You are already logged in!')
            return _json_redirect(request, url_from)
        login_nickname, login_password = None, None
        errors = {}
        if request.method == 'POST':
            login_nickname = _strip(request.POST.getone('login_nickname'))
            login_password = _strip(request.POST.getone('login_password'))
            validate_nickname(login_nickname, errors, 'login_nickname')
            validate_password(login_password, errors, 'login_password')
            if not errors:
                avatar = _login(request, login_nickname, login_password)
                if avatar:
                    _flash(request, WELCOME_MESSAGE % avatar.nickname)
                    return _json_redirect(request, url_from)
                else:
                    _add_error(errors, 'login_nickname', 'Incorrect nickname or password')
        return {'errors':errors,
                'login_nickname':login_nickname,
                'login_password':login_password}

    @action()
    def logout(self):
        request = self.request
        logout_and_purge_cookies(request)
        redirect_to = request.GET.get('from')
        if not redirect_to:
            redirect_to = route_url('home', request)
        return HTTPFound(location=redirect_to)

    @action(renderer='nickname.mak', xhr=True)
    def nickname(self):
        request = self.request
        url_from = request.GET.get('from', '/')
        if url_from == request.url:
            url_from = '/'
        changed_nickname = None
        errors = {}
        if request.method == 'POST':
            changed_nickname = _strip(request.POST.getone('changed_nickname'))
            validate_nickname(changed_nickname, errors, 'changed_nickname')
            avatar = _get_authenticated_or_anonymous_avatar(request)
            _validate_nickname_uniqueness(changed_nickname, errors, avatar, key='changed_nickname')
            if not errors:
                if avatar:
                    avatar.nickname = changed_nickname
                else:
                    avatar = _create_anonymous_avatar(request, changed_nickname)
                _flash(request, 'Your nickname has been updated')
                return _json_redirect(request, url_from)
        #url_nickname = route_url('nickname', request)
        return {'changed_nickname':changed_nickname,
                'errors':errors,
                'url_nickname':'/p/nickname'}

    @action(renderer='login.mak', xhr=True)
    def register(self):
        request = self.request
        url_from = request.GET.get('from', '/')
        if url_from == request.url:
            url_from = '/'
        avatar = _get_authenticated_avatar(request)
        if avatar:
            _flash(request, 'You must log out before attempting to register a new account')
            return _json_redirect()
        register_nickname, register_email, register_password, register_confirm_password = None, None, None, None
        errors = {}
        if request.method == 'POST':
            register_nickname = _strip(request.POST.getone('register_nickname'))
            register_email = _strip(request.POST.getone('register_email'))
            register_password = _strip(request.POST.getone('register_password'))
            register_confirm_password = _strip(request.POST.getone('register_confirm_password'))
            validate_nickname(register_nickname, errors, 'register_nickname')
            _validate_nickname_uniqueness(register_nickname, errors, key='register_nickname')
            if register_email:
                validate_email(register_email, errors, 'register_email')
            validate_password(register_password, errors, 'register_password')
            validate_password(register_confirm_password, errors, 'register_confirm_password')
            if register_password and register_confirm_password and register_password != register_confirm_password:
                errors['register_confirm_password'] = ('Passwords do not match',)
            if not errors:
                avatar = _create_avatar(request,
                                       register_nickname,
                                       register_password,
                                       register_email)
                _flash(request, WELCOME_MESSAGE % register_nickname)
                return _json_redirect(request, url_from)
        return {'errors':errors,
                'register_nickname':register_nickname,
                'register_email':register_email,
                'register_password':register_password,
                'register_confirm_password':register_confirm_password}