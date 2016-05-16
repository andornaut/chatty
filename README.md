--------------------------------------------------------------------------------
Getting Started
--------------------------------------------------------------------------------

- cd <directory containing this file>

- $venv/bin/python setup.py develop

- $venv/bin/populate_chatty development.ini

- $venv/bin/pserve development.ini


# install 
http://pylons.readthedocs.org/projects/akhet/en/latest/usage.html

pip install akhet amqplib kombu orbited twisted psycopg2 pyramid_beaker pyramid_handlers pyramid_mailer simplejson SQLAHelper WebError WebHelpers yolk 
#coverage docutils nose 


# RabbitMq
Install version 2.7+ from http://www.rabbitmq.com/server.html
rabbitmq-plugins enable rabbitmq_stomp 

# Run configs:
orbited --config orbited.cfg
pserve development.ini --reload 

# Debug configs:
pserve development.ini # Cannot use the "reload" flag with debug

Install amqp_client rabbit_stomp plugins from http://www.rabbitmq.com/plugins.html
# /etc/rabbitmq/rabbitmq.conf
RABBITMQ_PLUGINS_DIR='/etc/rabbitmq/plugins/'
SERVER_START_ARGS='-rabbit_stomp listeners [{"0.0.0.0",61613

# deps
libpq-dev

--------------------------------------------------------------------------------
HOWTOs
--------------------------------------------------------------------------------

1) Reset rabbitmq exchanges

rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl start_app

2) Reset db

dropdb chatty && createdb -O dev chatty && populate_chatty development.ini

--------------------------------------------------------------------------------
Workarounds
--------------------------------------------------------------------------------
1) Debug doesn't work in eclipse (works in PyCharm)

Install PasteScript: https://sourceforge.net/tracker/?func=detail&aid=3495786&group_id=85796&atid=577329
Replace "use = egg:waitress#main" with "use = egg:Paste#http" in development.ini

--------------------------------------------------------------------------------
TODO
--------------------------------------------------------------------------------

1) Anonymous avatar's are deleted in order to let a new user re-use their nicknames.
This breaks Message history b/c when the Avatar's are deleted the 'nickname' on the Messages
that they've posted will return ''. A workaround would be to use a before_delete event
(currently commented out) to update the Message obj with the Avatar's nickname
prior to deletion. 
ref. http://www.sqlalchemy.org/docs/07/orm/events.html#mapper-events

2) Nickname doesn't get cleared when the DB is reset (b/c) the session tables 
are still there.

3) Refactor so the server "post" view expects separate 'command' and 'message' params.
Parsing the input currently happens on both client and server - should be only client side.

4) Try out pyramid_simpleform