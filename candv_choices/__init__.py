# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from candv import Choices as _Choices, VerboseConstant
from django.db.models import SubfieldBase, CharField


LOG = logging.getLogger(__name__)


class ChoiceItem(VerboseConstant):

    def __unicode__(self):
        return self.name


class Choices(_Choices):

    constant_class = ChoiceItem


class ChoicesField(CharField):

    __metaclass__ = SubfieldBase

    def __init__(self, choices_class, *args, **kwargs):
        assert issubclass(choices_class, Choices)
        assert issubclass(choices_class.constant_class, ChoiceItem)

        default = kwargs.get('default')
        if default is not None:
            assert isinstance(default, ChoiceItem)
            kwargs['default'] = default.name

        kwargs['choices'] = choices_class.choices()
        kwargs['max_length'] = max(len(x) for x in choices_class.names())

        self.choices_class = choices_class
        super(ChoicesField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, self.choices_class.constant_class):
            return value
        return self.choices_class.get_by_name(value) if value else value

    def get_prep_value(self, value):
        return value.name if isinstance(value, ChoiceItem) else value

    def clean(self, value, model_instance):
        """
        Convert the value's type and run validation. Validation errors
        from to_python and validate are propagated. The correct value is
        returned if no error is raised.
        """
        value = self.to_python(value).name
        self.validate(value, model_instance)
        self.run_validators(value)
        return value

    def _get_flatchoices(self):
        """
        Flattened version of choices tuple.
        """
        return [
            (self.to_python(choice), value) for choice, value in self.choices
        ]
    flatchoices = property(_get_flatchoices)
