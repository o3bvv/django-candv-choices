# -*- coding: utf-8 -*-
from candv.base import Constant, ConstantsContainer

from django.db.models import SubfieldBase, CharField
from django.utils.six import with_metaclass
from django.utils.text import capfirst

from types import MethodType


from .forms import ChoicesField as ChoicesFormField


BLANK_CHOICE_DASH = ("", "---------", "")


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
            method = MethodType(_to_string, constant)
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
                (x.name, getattr(x, 'verbose_name', x.name) or x.name)
                for x in self.choices_class.constants()
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

    def formfield(self, form_class=None, choices_form_class=None, **kwargs):
        """
        Returns a django.forms.Field instance for this database Field.
        """
        defaults = {
            'required': not self.blank,
            'label': capfirst(self.verbose_name),
            'help_text': self.help_text,
        }
        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()

        include_blank = (self.blank or
                         not (self.has_default() or 'initial' in kwargs))

        choices = [BLANK_CHOICE_DASH, ] if include_blank else []
        choices.extend([
            (
                x.name,
                getattr(x, 'verbose_name', x.name) or x.name,
                getattr(x, 'help_text', None) or None
            )
            for x in self.choices_class.constants()
        ])

        defaults['choices'] = choices
        defaults['coerce'] = self.to_python

        if self.null:
            defaults['empty_value'] = None

        # Many of the subclass-specific formfield arguments (min_value,
        # max_value) don't apply for choice fields, so be sure to only pass
        # the values that TypedChoiceField will understand.
        for k in list(kwargs):
            if k not in ('coerce', 'empty_value', 'choices', 'required',
                         'widget', 'label', 'initial', 'help_text',
                         'error_messages', 'show_hidden_initial'):
                del kwargs[k]

        defaults.update(kwargs)
        form_class = choices_form_class or ChoicesFormField
        return form_class(**defaults)

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        from south.modelsinspector import introspector
        field_class = "django.db.models.fields.CharField"
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)
