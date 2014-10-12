# -*- coding: utf-8 -*-

import copy

from django.core import validators
from django.core.exceptions import ValidationError
from django.forms.fields import Field, ChoiceField as DjangoChoiceField
from django.utils.encoding import smart_text, force_text

from .widgets import Select


class ChoicesField(Field):
    widget = Select
    default_error_messages = DjangoChoiceField.default_error_messages

    def __init__(self, choices=None, **kwargs):
        self.coerce = kwargs.pop('coerce', lambda val: val)
        self.empty_value = kwargs.pop('empty_value', '')
        super(ChoicesField, self).__init__(**kwargs)
        self.choices = self.widget.choices = choices or ()

    def __deepcopy__(self, memo):
        result = super(ChoicesField, self).__deepcopy__(memo)
        result.choices = copy.deepcopy(self.choices, memo)
        return result

    def to_python(self, value):
        """
        Validates that the value is in self.choices and can be coerced to the
        right type.
        """
        value = '' if value in validators.EMPTY_VALUES else smart_text(value)
        if value == self.empty_value or value in validators.EMPTY_VALUES:
            return self.empty_value
        try:
            value = self.coerce(value)
        except (ValueError, TypeError, ValidationError):
            self._on_invalid_value(value)
        return value

    def validate(self, value):
        """
        Validates that the input is in self.choices.
        """
        super(ChoicesField, self).validate(value)
        if value and not self.valid_value(value):
            self._on_invalid_value(value)

    def valid_value(self, value):
        """
        Check if the provided value is a valid choice.
        """
        text_value = force_text(value)
        for option_value, option_label, option_title in self.choices:
            if value == option_value or text_value == force_text(option_value):
                return True
        return False

    def _on_invalid_value(self, value):
        raise ValidationError(
            self.error_messages['invalid_choice'],
            code='invalid_choice',
            params={'value': value},
        )
