from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.security import Everyone, Authenticated, forget
from zope.interface.declarations import implements

def logout_and_purge_cookies(request):
    def logout_callback(request, response):
        response.headerlist.extend(delete_headers)

    delete_headers = forget(request)
    # Alternative to request.response_XYZ
    request.add_response_callback(logout_callback)

class SessionAuthenticationPolicy(CallbackAuthenticationPolicy):
    implements(IAuthenticationPolicy)

    def __init__(self, identifier_name='auth_tkt'):
        self.identifier_name = identifier_name

    def _del_identity(self, request):
        if self.identifier_name in request.session:
            request.session.__delitem__(self.identifier_name)

    def _get_identity(self, request):
        return request.session.get(self.identifier_name)

    def _set_identity(self, request, identity):
        request.session[self.identifier_name] = identity

    def authenticated_userid(self, request):
        identity = self._get_identity(request)
        if identity is None:
            return None
        return identity['authenticated_userid']

    def effective_principals(self, request):
        effective_principals = [Everyone]
        identity = self._get_identity(request)
        if identity:
            userid = identity['authenticated_userid']
            if userid:
                effective_principals.append(Authenticated)
                effective_principals.append(userid)
                effective_principals.extend([])
        return effective_principals

    def remember(self, request, principal, **kw):
        identity = {'authenticated_userid':principal}
        self._set_identity(request, identity)
        return []

    def forget(self, request):
        self._del_identity(request)
        request.session.delete()
        return self._get_delete_headers(request.environ)


    def _get_delete_headers(self, environ):
        from chatty import ENCRYPTION_COOKIE_NAME
        domain = environ.get('HTTP_HOST', environ.get('SERVER_NAME'))
        expire_age = "; Max-Age=0; Expires=Wed, 31-Dec-97 23:59:59 GMT"
        headers = [
            ('Set-Cookie', '%s="%s"; Path=/%s' % (ENCRYPTION_COOKIE_NAME,
                                                  '',
                                                  expire_age)),
            ('Set-Cookie', '%s="%s"; Path=/; Domain=%s%s' % (ENCRYPTION_COOKIE_NAME,
                                                            '',
                                                            domain,
                                                            expire_age))
            ]
        return headers