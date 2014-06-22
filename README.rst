django-candv-choices
====================

|PyPi package| |Downloads|

Use complex constants built with `candv`_ library instead of standard `choices`_
fields for `Django`_ models.

Live demo
---------

Try `online live demo <http://django-candv-choices.herokuapp.com/>`_! Use
``demo``/``demo`` as login/pass for authentication.

|Demo preview|

Installation
------------

Install from `PyPI <https://pypi.python.org/pypi/django-candv-choices>`_:

.. code-block:: bash

    $ pip install django-candv-choices


Problem overview
----------------

Well, you need to define some constant choices for your Django model field.
Let's start from defining constants themselves:

.. code-block:: python

    # constants.py
    from django.utils.translation import ugettext_lazy as _

    AUTH_TYPE_BASIC = 'BASIC'
    AUTH_TYPE_DIGEST = 'DIGEST'
    AUTH_TYPE_CLIENT_CERT = 'CLIENT-CERT'
    AUTH_TYPE_FORM = 'FORM'

    AUTH_TYPES = (
        (AUTH_TYPE_BASIC, _("HTTP Basic Authentication")),
        (AUTH_TYPE_DIGEST, _("HTTP Digest Authentication ")),
        (AUTH_TYPE_CLIENT_CERT, _("HTTPS Client Authentication ")),
        (AUTH_TYPE_FORM, _("Form Based Authentication ")),
    )

Here we define constant names and attach verbose names to them. Bloated
definition, no docstring for constants group, no docstings per constant. What if
you need to define some help text per constant? 4 more definitions? Well, then
just imagine, how you will attach them. And what about other attributes?
And what about adding some methods for constants? How about getting constant by
its name? By value? And how about performing some operations on the whole
constants group?

Only at this point you may end up with one big module which will work only with
one group of constants. And this work will be a big pain.

But OK, let's go further and define some DB model field:

.. code-block:: python

    # models.py
    from django.db import models
    from django.utils.translation import ugettext_lazy as _

    from . constants import AUTH_TYPES, AUTH_TYPE_BASIC


    class Request(models.Model):

        auth_type = models.CharField(
            verbose_name=_("Auth type"),
            help_text=_("Example of default constants"),
            choices=AUTH_TYPES,
            blank=False,
            max_length=11,
            default=AUTH_TYPE_BASIC)

3 things to mention here:

* you have to import constant group itself;
* you may have to import dafault value too;
* you need go back to constants definition, iterate over each constant,
  calculate its length and select the longest value to pass it as ``max_length``
  argument. And don't try to make a mistake, or you will be punished otherwise.

I use ``CharField`` here intentionally. It can be good to use ``IntegerField``,
``PositiveSmallIntegerField`` and so on, but it is very probable that you will
be willing someone to kill you due to hidden bugs.

Now it's showtime! Let's render our field:

.. code-block:: jinja

    <ul>
    {% for r in requests %}
      <li>{{ r.auth_type }}</li>
    {% endfor %}
    </ul>

What do you see? ``BASIC``, ``DIGEST``, ``FORM``, etc. Oops! How to get our
human messages like ``HTTP Basic Authentication``?

You need to convert constants group to ``dict`` and pass it to template's
context! But wait, this is not the end. You can not access dict values directly
within templates. You need to create a library of template tags, register a
filter and load the library to template:

.. code-block:: python

    # templatetags/custom_tags.py
    from django import template

    register = template.Library()


    @register.filter
    def lookup(d, key):
        return d[key]


.. code-block:: jinja

    {% load custom_tags %}
    <ul>
    {% for r in requests %}
      <li>{{ AUTH_TYPES|lookup:r.auth_type }}</li>
    {% endfor %}
    </ul>


This is madness!

Solution
--------

# Coming today soon

Affects
-------

# Coming today soon

TODO
----

# Coming today soon

Changelog
---------

* `1.0.0`_ (Jun 22, 2014)

  Initial version


.. |PyPi package| image:: https://badge.fury.io/py/django-candv-choices.png
   :target: http://badge.fury.io/py/django-candv-choices/
.. |Downloads| image:: https://pypip.in/d/django-candv-choices/badge.png
   :target: https://crate.io/packages/django-candv-choices/

.. |Demo preview| image:: http://i.imgur.com/NXKsgRA.png
   :target: http://django-candv-choices.herokuapp.com/
   :alt: Live demo screenshot

.. _candv: http://candv.readthedocs.org/en/latest/
.. _choices: https://docs.djangoproject.com/en/1.6/ref/models/fields/#django.db.models.Field.choices
.. _Django: https://www.djangoproject.com/

.. _1.0.0: https://github.com/oblalex/django-candv-choices/releases/tag/v1.0.0
