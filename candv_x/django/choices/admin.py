# -*- coding: utf-8 -*-
from django.contrib.admin.filters import (
    FieldListFilter, ChoicesFieldListFilter as DjangoChoicesFieldListFilter,
)

from django.utils.encoding import force_text, smart_text
from django.utils.translation import ugettext_lazy as _

from .db import ChoicesField


class ChoicesFieldListFilter(DjangoChoicesFieldListFilter):
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
            'display': force_text(title),
        }

        yield _choice_item(
            self.lookup_val is None,
            cl.get_query_string({}, [self.lookup_kwarg]),
            _('All'))
        container = (self.field.choices
                     if isinstance(self.field, ChoicesField) else
                     self.field.flatchoices)
        for lookup, title in container:
            yield _choice_item(
                smart_text(lookup) == self.lookup_val,
                cl.get_query_string({self.lookup_kwarg: lookup}),
                title)


FieldListFilter.register(lambda field: bool(field.choices),
                         ChoicesFieldListFilter,
                         take_priority=True)
