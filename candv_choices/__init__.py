# -*- coding: utf-8 -*-
"""
Adds support for custom complex choices for Django models.
"""
from candv import VerboseConstant
from candv.base import ConstantsContainer

from django.contrib.admin.filters import (
    FieldListFilter, ChoicesFieldListFilter as _ChoicesFieldListFilter,
)
from django.db.models import SubfieldBase, CharField

from django.utils.encoding import smart_text
from django.utils.six import with_metaclass
from django.utils.translation import ugettext_lazy as _


class ChoiceItem(VerboseConstant):

    def __unicode__(self):
        """
        This will be used as value for <option> tag.
        """
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
        return tuple((name, x.verbose_name or name) for name, x in cls.items())


class ChoicesField(with_metaclass(SubfieldBase, CharField)):

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
        #: return constant's name instead of constant itself
        value = self.to_python(value).name
        self.validate(value, model_instance)
        self.run_validators(value)
        return value

    def _get_flatchoices(self):
        """
        Flattened version of choices tuple.

        Need to return constants themselves instead of their names for right
        rendering in admin's 'change_list' view, if field is present in
        'list_display' attribute of model's admin.
        """
        return [
            (self.to_python(choice), value) for choice, value in self._choices
        ]
    flatchoices = property(_get_flatchoices)


class ChoicesFieldListFilter(_ChoicesFieldListFilter):
    """
    Redefine standard 'ChoicesFieldListFilter'.
    """
    def choices(self, cl):
        """
        Take choices from field's 'choices' attribute for 'ChoicesField' and
        use 'flatchoices' as usual for other fields.
        """
        #: Just tidy up standard implementation for the sake of DRY principle.
        _choice_item = lambda is_selected, query_string, title: {
            'selected': is_selected,
            'query_string': query_string,
            'display': title
        }

        yield _choice_item(self.lookup_val is None,
                           cl.get_query_string({}, [self.lookup_kwarg]),
                           _('All'))
        container = (self.field.choices
                     if isinstance(self.field, ChoicesField) else
                     self.field.flatchoices)
        for lookup, title in container:
            yield _choice_item(smart_text(lookup) == self.lookup_val,
                               cl.get_query_string({self.lookup_kwarg: lookup}),
                               title)


FieldListFilter.register(lambda f: bool(f.choices),
                         ChoicesFieldListFilter,
                         take_priority=True)
