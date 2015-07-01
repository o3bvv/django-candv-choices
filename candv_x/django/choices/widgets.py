# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import chain

from candv.base import Constant

from django import VERSION as django_version

from django.forms.widgets import Widget
from django.utils.encoding import force_text
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe

# Use old path for form utils if Django version < 1.7
if django_version[0] <= 1 and django_version[1] < 7:
    from django.forms.util import flatatt
else:
    from django.forms.utils import flatatt


class Select(Widget):

    def __init__(self, attrs=None, choices=None):
        super(Select, self).__init__(attrs)
        self.choices = list(choices or [])

    def render(self, name, value, attrs=None, choices=None):
        choices = choices or ()

        if value is None:
            value = ''
        elif isinstance(value, Constant):
            value = value.name

        final_attrs = self.build_attrs(attrs, name=name)
        output = [
            '<select{0}>'.format(flatatt(final_attrs)),
        ]
        options = self.render_options(choices, value)
        if options:
            output.append(options)
        output.append('</select>')

        return mark_safe('\n'.join(output))

    def render_options(self, choices, selected_choice):
        selected_choice = force_text(selected_choice)
        output = []
        for value, label, title in chain(self.choices, choices):
            value = force_text(value)
            ensure_title = (
                ' title="{0}"'.format(conditional_escape(force_text(title)))
                if title else
                '')
            ensure_selected = (
                ' selected="selected"'
                if value == selected_choice else
                '')
            option = (
                '<option value="{0}"{1}{2}>{3}</option>'
                .format(
                    escape(value),
                    ensure_title,
                    ensure_selected,
                    conditional_escape(force_text(label))
                ))
            output.append(option)
        return '\n'.join(output)
