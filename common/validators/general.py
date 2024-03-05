import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class ListFieldValidator(validators.RegexValidator):
    regex = r'^(\[.*?\]|null)$'
    message = _(
        'List field only accepts list-like or null string'
    )
    flags = re.UNICODE


@deconstructible
class DictFieldValidator(validators.RegexValidator):
    regex = r'^(\{.*?\}|null)$'
    message = _(
        'Enter a valid username. This value may contain only English letters, '
        'numbers, and @/./+/-/_ characters.'
    )
    flags = re.UNICODE


@deconstructible
class ClassNameValidator(validators.RegexValidator):
    regex = r'^([A-Z]|_){1}[a-zA-Z0-9_]?'
    message = _('An invalid class name received.')


@deconstructible
class DateStringValidator(validators.RegexValidator):
    """
    2022-10-20
    """
    regex = r'\d{4}-[0-1]\d{1}-[0-3]\d{1}'
    message = _('Enter a valid date string, like 2000-06-01.')


@deconstructible
class YearStringValidator(validators.RegexValidator):
    """
    1 - 3000
    """
    regex = r'[1-2]{1}[0-9]{3}'  # 1000 - 2999
    message = _('Enter a valid year string, like 2001.')


@deconstructible
class MonthStringValidator(validators.RegexValidator):
    """
    1 - 12
    """
    regex = r'0[1-9]|1[0-2]'
    message = _('Enter a valid month string, like 06.')
