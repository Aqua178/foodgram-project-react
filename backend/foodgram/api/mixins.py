import re

from django.core.exceptions import ValidationError

USERNAME_REGEX = r'[\w\.@+-]+'
SLUG_REGEX = r'^[-a-zA-Z0-9_]+$'
NOT_ALLOWED_ME = ('Нельзя создать пользователя с '
                  'именем: << {username} >> - это имя запрещено!')
NOT_ALLOWED_CHAR_MSG_USERNAME = ('{chars} недопустимые символы '
                                 'в имени пользователя {username}.')

NOT_ALLOWED_CHAR_MSG_SLUG = ('{chars} недопустимые символы '
                             'в слаге тега {slug}.')


def validate_username(username):
    invalid_symbols = ''.join(set(re.sub(USERNAME_REGEX, '', username)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_CHAR_MSG_USERNAME.format(
                chars=invalid_symbols, username=username))
    if username == 'me':
        raise ValidationError(NOT_ALLOWED_ME.format(username=username))
    return username


def validate_slug(slug):
    invalid_symbols = ''.join(set(re.sub(SLUG_REGEX, '', slug)))
    if invalid_symbols:
        raise ValidationError(
            NOT_ALLOWED_CHAR_MSG_SLUG.format(
                chars=invalid_symbols, username=slug))
    return slug
