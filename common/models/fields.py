import json

from common.validators.general import ListFieldValidator, DictFieldValidator
from django.core.exceptions import ValidationError
from django.db import models


class JsonField(models.TextField):
    max_length = 2048

    def __init__(self, *args, **kwargs):
        max_length = kwargs.pop('max_length') if 'max_length' in kwargs else self.max_length
        self.encoder = kwargs.pop('encoder', json.JSONEncoder)
        super().__init__(*args, max_length=max_length, **kwargs)

    def get_prep_value(self, value):
        # before saving to db, value could be a string or Promise
        if value is None:
            return value
        # call super method to internationalize value
        value = super().get_prep_value(value)
        # here, value could be a python object
        if isinstance(value, Exception):
            raise value
        return json.dumps(value, cls=self.encoder)

    def from_db_value(self, value, *_):
        return self.to_python(value)

    def to_python(self, value):
        if isinstance(value, (dict, list)):
            return value
        else:
            if value is None:
                return
            try:
                return json.loads(value)
            except json.decoder.JSONDecodeError:
                return ValidationError(
                    self.error_messages['invalid'],
                    code='invalid',
                    params={'value': value}
                )

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if value is None:
            return
        return json.dumps(value, cls=self.encoder)


class ListField(JsonField):
    description = 'list'
    default_error_messages = {
        'invalid': 'value must be a list-like jsonable string or null'
    }
    default_validators = [ListFieldValidator()]
    empty_values = [[], None, '[]']

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if value is None:
            return
        try:
            return json.dumps(value, cls=self.encoder)
        except TypeError:
            return '[]'  # blank

    def to_python(self, value):
        if isinstance(value, str) and not value:
            return list()
        return super().to_python(value)

    def get_default(self):
        return []


class DictField(JsonField):
    description = 'Dict'
    default_error_messages = {
        'invalid': 'value must be a dict-like jsonable string or null'
    }
    default_validators = [DictFieldValidator()]
    empty_values = [{}, None, '{}']

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        if value is None:
            return
        try:
            return json.dumps(value, cls=self.encoder)
        except TypeError:
            return '{}'  # blank

    def to_python(self, value):
        if isinstance(value, str) and not value:
            return dict()
        return super().to_python(value)

    def get_default(self):
        return {}
