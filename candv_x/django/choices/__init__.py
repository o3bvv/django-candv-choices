# -*- coding: utf-8 -*-
"""
Adds support for custom complex choices for Django models.
"""
from candv.base import Constant, ConstantsContainer

from django.contrib.admin.filters import (
    FieldListFilter, ChoicesFieldListFilter as _ChoicesFieldListFilter,
)
from django.db.models import SubfieldBase, CharField

from django.utils.encoding import smart_text
from django.utils.six import with_metaclass
from django.utils.translation import ugettext_lazy as _

from types import MethodType


class ChoicesField(with_metaclass(SubfieldBase, CharField)):
    """
    Database field for storying candv-based constants.
    """
    def __init__(self, choices, *args, **kwargs):
        assert issubclass(choices, ConstantsContainer)
        assert issubclass(choices.constant_class, Constant)

        default = kwargs.get('default')
        if default is not None:
            assert isinstance(default, Constant)
            kwargs['default'] = default.name

        self._patch_items(choices)
        self.choices_class = choices

        kwargs.pop('choices', None)
        kwargs['max_length'] = max(len(x) for x in choices.names())

        super(ChoicesField, self).__init__(*args, **kwargs)

    def _patch_items(self, choices):

        def _to_string(self):
            return self.name

        for constant in choices.iterconstants():
            #: Render propper value for <option> tag.
            method = MethodType(_to_string, constant, constant.__class__)
            setattr(constant, '__str__', method)
            setattr(constant, '__unicode__', method)

    def to_python(self, value):
        if isinstance(value, self.choices_class.constant_class):
            return value
        return self.choices_class[value] if value else value

    def get_prep_value(self, value):
        return value.name if isinstance(value, Constant) else value

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

    def _get_choices(self):
        """
        Redefine standard method.
        """
        if not self._choices:
            self._choices = tuple(
                (name, getattr(item, 'verbose_name', name) or name)
                for name, item in self.choices_class.items()
            )
        return self._choices
    choices = property(_get_choices)

    def _get_flatchoices(self):
        """
        Redefine standard method.

        Return constants themselves instead of their names for right rendering
        in admin's 'change_list' view, if field is present in 'list_display'
        attribute of model's admin.
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


FieldListFilter.register(lambda field: bool(field.choices),
                         ChoicesFieldListFilter,
                         take_priority=True)
