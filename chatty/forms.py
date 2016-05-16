import logging
import re

log = logging.getLogger(__name__)

EMAIL_REGEX_MSG = 'This isn\'t a valid address. (You can leave it blank)'
EMAIL_REGEX = re.compile('^([\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+\.)*[\w\!\#$\%\&\'\*\+\-\/\=\?\^\`{\|\}\~]+@((((([a-z0-9]{1}[a-z0-9\-]{0,62}[a-z0-9]{1})|[a-z])\.)+[a-z]{2,6})|(\d{1,3}\.){3}\d{1,3}(\:\d{1,5})?)$')
EMAIL_MIN_LENGTH = 4
EMAIL_MAX_LENGTH = 255
MESSAGE_MAX_LENGTH = 4096
NICKNAME_REGEX_MSG = 'Must contain only letters, numbers, and some symbols'
NICKNAME_REGEX = re.compile('^[\w\-\_]+$')
NICKNAME_MIN_LENGTH = 3
NICKNAME_MAX_LENGTH = 50
PASSWORD_MIN_LENGTH = 3
PASSWORD_MAX_LENGTH = 100
TITLE_REGEX_MSG = 'Must contain only letters, numbers, single spaces and some symbols'
TITLE_REGEX = re.compile('^[\w\.\'\-\_]+(([\s]?[\w\.\'\-\_]+)+)*$')
TITLE_MIN_LENGTH = 3
TITLE_MAX_LENGTH = 200
TOPIC_MIN_LENGTH = 3
TOPIC_MAX_LENGTH = 500

def _is_submitted(value, errors):
    if value is None or len(value) == 0:
        errors.append('This field is required')
        return False
    return True

def _process_errors(key, dictionary, errors):
    if dictionary is not None:
        if errors:
            if key in dictionary:
                dictionary[key].extend(errors)
            else:
                dictionary[key] = errors
    else:
        return errors or []

def _validate_min_max(value, errors, min=None, max=None):
    assert(min is not None or max is not None)
    value_len = len(value)
    if min and value_len < min:
        errors.append('Must contain at least %s characters' % min)
    elif max and value_len > max:
        errors.append('Must contain fewer than %s characters' % max)

def _validate_regex(value, errors, regex, message):
    if not re.match(regex, value):
        errors.append(message)

def validate_message(value, dictionary=None, key='body'):
    errors = []
    _validate_min_max(value, errors, max=MESSAGE_MAX_LENGTH)
    return _process_errors(key, dictionary, errors)

def validate_email(value, dictionary=None, key='email'):
    errors = []
    _validate_min_max(value, errors, EMAIL_MIN_LENGTH, EMAIL_MAX_LENGTH)
    _validate_regex(value, errors, EMAIL_REGEX, EMAIL_REGEX_MSG)
    return _process_errors(key, dictionary, errors)

def validate_nickname(value, dictionary=None, key='nickname'):
    errors = []
    if _is_submitted(value, errors):
        _validate_min_max(value, errors, NICKNAME_MIN_LENGTH, NICKNAME_MAX_LENGTH)
        _validate_regex(value, errors, NICKNAME_REGEX, NICKNAME_REGEX_MSG)
    return _process_errors(key, dictionary, errors)

def validate_password(value, dictionary=None, key='password'):
    errors = []
    if _is_submitted(value, errors):
        _validate_min_max(value, errors, PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH)
        if ' ' in value:
            errors.append('Cannot contain spaces')
    return _process_errors(key, dictionary, errors)

def validate_title(value, dictionary=None, key='title'):
    errors = []
    if _is_submitted(value, errors):
        _validate_min_max(value, errors, TITLE_MIN_LENGTH, TITLE_MAX_LENGTH)
        _validate_regex(value, errors, TITLE_REGEX, TITLE_REGEX_MSG)
    return _process_errors(key, dictionary, errors)

def validate_topic(topic, dictionary=None, key='topic'):
    errors = []
    _validate_min_max(topic, errors, TOPIC_MIN_LENGTH, TOPIC_MAX_LENGTH)
    return _process_errors(key, dictionary, errors)