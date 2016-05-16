from chatty.authentication import logout_and_purge_cookies
from chatty.commands import ResponseHelper
from chatty.models import Avatar, DBSession
from chatty.utils import now
from pyramid.response import Response
from pyramid.security import authenticated_userid, remember
from sqlalchemy.orm.exc import NoResultFound
import simplejson

def _get_anonymous_avatar(request):
    session = request.session
    anonymous_avatar_id = session.get('anonymous_avatar_id')
    if anonymous_avatar_id:
        avatar = Avatar.with_anonymous_id(anonymous_avatar_id)
        if avatar:
            avatar.accessed = now()
            return avatar
        else:
            _flash(request, 'Your session is no longer available. Please set your nickname or <a href="/p/login" class="login" title="Login / Register">login</a>.')
            logout_and_purge_cookies(request)


def _get_authenticated_avatar(request):
    authenticated_id = authenticated_userid(request)
    if authenticated_id:
        avatar = Avatar.with_id(authenticated_id)
        if avatar:
            avatar.accessed = now()
            return avatar
        else:
            _flash(request, 'Your account is no longer available. Please contact us for more information.')
            logout_and_purge_cookies(request)

def _get_authenticated_or_anonymous_avatar(request):
    return _get_authenticated_avatar(request) or _get_anonymous_avatar(request)

def _add_error(errors, key, msg):
    if key in errors:
        errors[key].append(msg)
    else:
        errors[key] = [msg]

def _create_anonymous_avatar(request, nickname):
    assert 'is_authenticated' not in request.session
    avatar = Avatar(nickname=nickname)
    avatar.create_private_key(request.session.id)
    DBSession.add(avatar)
    DBSession.flush()
    request.session['anonymous_avatar_id'] = avatar.id
    request.session['nickname'] = avatar.nickname
    return avatar

def _create_avatar(request, nickname, password, email=None):
    avatar = Avatar(nickname=nickname,
                    email=email)
    avatar.set_password(password)
    DBSession.add(avatar)
    DBSession.flush()
    avatar = _login(request, nickname, password)
    assert avatar
    return avatar

def _flash(request, message):
    session = request.session
    session['flash'] = message
    session.save()

def _json_redirect(request, url):
    dictionary = ResponseHelper.redirect(url)
    json_body = simplejson.dumps(dictionary)
    return Response(body=json_body, content_type='text/json', request=request)

def _login(request, nickname, password):
    try:
        avatar = Avatar.with_nickname(nickname)
        if not avatar.is_anonymous and avatar.check_password(password):
            if 'anonymous_avatar_id' in request.session:
                del request.session['anonymous_avatar_id']
            request.session['is_authenticated'] = True
            request.session['nickname'] = avatar.nickname
            remember(request, avatar.id)
            avatar.create_private_key(request.session.id)
            avatar.last_login = now()
            return avatar
    except NoResultFound:
        pass


def _validate_nickname_uniqueness(nickname, errors, avatar=None, key='nickname'):
    try:
        existing = Avatar.with_nickname(nickname)
        if existing:
            if avatar and avatar.id == existing.id:
                _add_error(errors,
                          key,
                          'Your nickname is already %s' % nickname)
            elif not existing.is_anonymous:
                _add_error(errors,
                          key,
                          'Nickname is already registered. If you have registered this nickname, then try logging in.')
            elif not existing.is_deletable:
                _add_error(errors,
                          key,
                          'Nickname currently in use. It may become available if the current user logs off before registering it.')
            else:
                DBSession.delete(existing)
                DBSession.flush()
    except NoResultFound:
        pass

def _strip(value):
    if value and hasattr(value, 'strip'):
        value = value.strip()
    return value


class Handler(object):
    def __init__(self, request):
        self.request = request


def includeme(config):
    """Add the application's view handlers.
    """
    config.add_handler('home', '/',
                       'chatty.handlers.main.MainHandler',
                       action='home')
    config.add_handler('main', '/p/{action}',
                       'chatty.handlers.main.MainHandler')

    config.add_handler('conversations-view', '/{title}',
                       'chatty.handlers.conversation.ConversationHandler',
                       action='view',
                       path_info=r'/(?!favicon\.ico|robots\.txt|w3c)')
    config.add_handler('conversations-view-latest', '/{title}/latest',
                       'chatty.handlers.conversation.ConversationHandler',
                       action='view_latest')
    config.add_handler('conversations-view-before-message', '/{title}/before/{message_id}',
                       'chatty.handlers.conversation.ConversationHandler',
                       action='view_before_message')
    config.add_handler('conversations-post', '/{title}/post',
                       'chatty.handlers.conversation.ConversationHandler',
                       action='post')