django-candv-choices
====================

|PyPi package| |Downloads|

Use complex constants built with `candv`_ library instead of standard `choices`_
fields for `Django`_ models.

Try `online live demo <http://django-candv-choices.herokuapp.com/>`_! Use
``demo``/``demo`` as login/pass for authentication.

|Demo preview|


**Table of contents**

.. contents::
    :local:
    :depth: 1
    :backlinks: none


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

The solution is to use `candv`_ and this library. The former allows you to
define stand-alone groups of complex constants and latter allows you to use
those constants as choises.

Let's examine some simple example and define some constants:

.. code-block:: python

    # constants.py
    from candv import SimpleConstant, Constants

    class METHOD_TYPE(Constants):
        """
        Available HTTP methods.
        """
        GET = SimpleConstant()
        PUT = SimpleConstant()
        POST = SimpleConstant()
        DELETE = SimpleConstant()
        TRACE = SimpleConstant()

Here we defined a group of constants with no attributes. Looks pretty, let's use
it:

.. code-block:: python

    # models.py
    from candv_choices import ChoicesField

    from django.db import models
    from django.utils.translation import ugettext_lazy as _

    from . constants import METHOD_TYPE

    class Request(models.Model):

        method = ChoicesField(
            verbose_name=_("method"),
            help_text=_("Example of simple candv constants"),
            choices=METHOD_TYPE,
            blank=False,
        )

That's all. You can pass some default value if you want,
e.g. ``default=METHOD_TYPE.GET``.

Now you can render it:

.. code-block:: jinja

    <ul>
    {% for r in requests %}
      <li>{{ r.method.name }}</li>
    {% endfor %}
    </ul>

The output will contain ``GET``, ``PUT``, ``POST``, etc. Want more? Let's add
values, verbose names and help texts:

.. code-block:: python

    # constants.py
    from candv import VerboseValueConstant, Values
    from django.utils.translation import ugettext_lazy as _

    class RESULT_TYPE(Values):
        """
        Possible operation results.
        """
        SUCCESS = VerboseValueConstant(
            value='2C7517',
            verbose_name=_("Success"),
            help_text=_("Yay! Everything is good!")
        )
        FAILURE = VerboseValueConstant(
            value='A30D0D',
            verbose_name=_("Failure"),
            help_text=_("Oops! Something went wrong!")
        )
        PENDING = VerboseValueConstant(
            value='E09F26',
            verbose_name=_("Pending"),
            help_text=_("Still waiting for the task to complete...")
        )

..

    Please, refer to `candv usage`_ to learn how to define and use constants.
    You may find `candv customization`_ useful too.

Here we have used `Values`_ as container and `VerboseValueConstant`_ as class
for items. Each constant has a ``name`` (e.g. ``SUCCESS``), a value, a verbose
text and a help text. All of this you can access directly from everywhere.

Field definition does not differ much from previous:

.. code-block:: python

    # models.py
    from candv_choices import ChoicesField

    from django.db import models
    from django.utils.translation import ugettext_lazy as _

    from . constants import RESULT_TYPE

    class Request(models.Model):

        result = ChoicesField(
                verbose_name=_("result"),
                help_text=_("Example of complex candv constants with verbose names, "
                            "help texts and inner values"),
                choices=RESULT_TYPE,
                blank=False,
                default=RESULT_TYPE.SUCCESS,
            )

You may use ``blank=True`` if you wish, there's no problem. Let's output our
data:

.. code-block:: jinja

    <table>
    {% for r in requests %}
      <tr>
        <td style="color: #{{ r.result.value }};" title="{{ r.result.help_text }}">
          {{ r.result.verbose_name }}
        </td>
      </tr>
    {% endfor %}
    </table>

Not so hard, innit?

You can pass any constants to ``ChoicesField`` from your old projects or
external libraries. Enjoy!

Caveats
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

.. _Values: http://candv.readthedocs.org/en/latest/candv.html#candv.Values
.. _VerboseValueConstant: http://candv.readthedocs.org/en/latest/candv.html#candv.VerboseValueConstant

.. _candv usage: http://candv.readthedocs.org/en/latest/usage.html#usage
.. _candv customization: http://candv.readthedocs.org/en/latest/customization.html

.. _1.0.0: https://github.com/oblalex/django-candv-choices/releases/tag/v1.0.0
