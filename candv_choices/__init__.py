# -*- coding: utf-8 -*-
"""
Adds support for custom complex choices for Django models.
"""
from candv import VerboseConstant
from candv.base import ConstantsContainer

from django.db.models import SubfieldBase, CharField


class ChoiceItem(VerboseConstant):

    def __unicode__(self):
        return self.name


class Choices(ConstantsContainer):
    """
    Container of instances of :class:`VerboseConstant` and it's subclasses.

    Provides support for building `Django-compatible <https://docs.djangoproject.com/en/1.6/ref/models/fields/#choices>`_
    choices.
    """
    #: Set `ChoiceItem` as top-level class for this container.
    #: See `candv.base.ConstantsContainer.constant_class`.
    constant_class = ChoiceItem

    @classmethod
    def choices(cls):
        """
        Get a tuple of tuples representing constant's name and its verbose name.

        :returns: a tuple of constant's names and their verbose names in order
                  they were defined.

        **Example**::

            >>> from candv import Choices, VerboseConstant
            >>> class FOO(Choices):
            ...     ONE = VerboseConstant("first", help_text="first choice")
            ...     FOUR = VerboseConstant("fourth")
            ...     THREE = VerboseConstant("third")
            ...
            >>> FOO.choices()
            (('ONE', 'first'), ('FOUR', 'fourth'), ('THREE', 'third'))
            >>> FOO.get_by_name('ONE').help_text
            'first choice'
        """
        return tuple((name, x.verbose_name) for name, x in cls.items())


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
