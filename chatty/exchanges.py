from kombu.connection import BrokerConnection
from kombu.entity import Exchange
from kombu.messaging import Producer
import logging

log = logging.getLogger(__name__)

PRIVATE_NAME = 'private'
PRIVATE_TYPE = 'direct'
PUBLIC_NAME = 'conversation'
PUBLIC_TYPE = 'fanout'

class ExchangeService(object):
    def __enter__(self):
        self.connection = BrokerConnection()
        self.channel = self.connection.channel()
        return self.channel

    def __exit__(self, exc_type, exc_value, traceback):
        self.channel.close()
        self.connection.close()

    def setup_exchanges(self):
        try:
            with self as channel:
                exchange = Exchange(name=PUBLIC_NAME,
                                    type=PUBLIC_TYPE)
                Producer(channel, exchange)
                exchange = Exchange(name=PRIVATE_NAME,
                                    type=PRIVATE_TYPE)
                Producer(channel, exchange)
        except Exception as e:
            log.error(e)

    def send_public(self, name, message):
        try:
            with self as channel:
                exchange = Exchange(name=PUBLIC_NAME,
                                    type=PUBLIC_TYPE)
                producer = Producer(channel, exchange, routing_key=name)
                producer.publish(message)
        except Exception as e:
            log.error(e)

    def send_private(self, name, message):
        try:
            with self as channel:
                exchange = Exchange(name=PRIVATE_NAME,
                                    type=PRIVATE_TYPE)
                producer = Producer(channel, exchange, routing_key=name)
                producer.publish(message)
        except Exception as e:
            log.error(e)

EXCHANGE = ExchangeService()