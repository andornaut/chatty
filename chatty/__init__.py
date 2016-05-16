from .models import DBSession
from akhet.static import add_static_route
from chatty.exchanges import EXCHANGE
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid_mailer.mailer import Mailer
from sqlalchemy import engine_from_config
import pyramid_beaker


#AMPQ Server Info
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 5672
BROKER_VHOST = "/"
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
ORIBTED_STATIC_PORT = 9000
ORBITED_STOMP_PORT = 61613

#chatty settings
ENCRYPTION_COOKIE_NAME = 'chatty-store'

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    EXCHANGE.setup_exchanges()

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    config = Configurator(authentication_policy=SessionAuthenticationPolicy(),
                          authorization_policy=ACLAuthorizationPolicy(),
                          settings=settings)
    config.include("pyramid_handlers")
    config.include("chatty.handlers")
    config.include('akhet')
    config.scan()

    # http://docs.pylonsproject.org/thirdparty/pyramid_mailer/dev/
    # Get mailer with:  mailer = request.registry['mailer'] 
    config.registry['mailer'] = Mailer.from_settings(settings)

    # Configure Beaker sessions
    session_factory = pyramid_beaker.session_factory_from_settings(settings)
    config.set_session_factory(session_factory)
    pyramid_beaker.set_cache_regions_from_settings(settings)

    # Configure Subscribers
    config.add_subscriber('chatty.subscribers.add_renderer_globals',
                          'pyramid.events.BeforeRender')
    # Set up routes and views
    # Arg 1 is the Python package containing the static files.
    # Arg 2 is the subdirectory in the package containing the files.    
    config.add_static_route('chatty', 'static', cache_max_age=3600)

    return config.make_wsgi_app()