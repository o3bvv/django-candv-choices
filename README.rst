django-candv-choices
====================

|pypi_package| |pypi_downloads| |python_versions| |license|

Use complex constants built with `candv`_ library instead of standard
`choices`_ fields for `Django`_ models.

Try `online live demo <http://django-candv-choices.herokuapp.com/>`_! Use
``demo``/``demo`` as login/pass for authentication.

|demo_preview|


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
definition, no docstring for constants group, no docstings per constant. What
if you need to define some help text per constant? 4 more definitions? Well,
then just imagine, how you will attach them. And what about other attributes?
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
  calculate its length and select the longest value to pass it as
  ``max_length`` argument. And don't try to make a mistake, or you will be
  punished otherwise.

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

Here we defined a group of constants with no attributes. Looks pretty, let's
use it:

.. code-block:: python

    # models.py
    from candv_x.django.choices import ChoicesField

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
    from candv_x.django.choices import ChoicesField

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

* Django admin renders choices by converting them to strings. So,
  ``__str__`` and ``__unicode__`` methods will be automatically overriden for
  constant items. It will return the name of the constant. By default,
  constants in ``candv`` do not have those methods at all (I cannot find a
  reason why the should to), so it seems not to be a problem. Just be aware.
* ``candv`` supports creating `hierarchies of constants`_. If you have some
  reason to use them as choices for DB field, take into accout that choices
  will be built only from top-level group of constants.


Things to think about
---------------------

* Django has `MultipleChoiceField`_ and `TypedMultipleChoiceField`_. I haven't
  used used them, but I think it can be useful to implement analogues for
  'candv', especially for ``MultipleChoiceField``.
* I think, there is a place to think about implementation of full support of
  hierarchies. Maybe it's possible to make some nested choices, or at least
  flatten them.


Changelog
---------

*You can click a version name to see a diff with the previous one.*

* `1.1.5`_ (Aug 1, 2015)

  * Fix usage of default values for migrations in Django >= 1.7
    (`issue #8`_).
  * Implement field serializer for restframework as a separate library
    `django-rf-candv-choices`_ (`issue #9`_).

* `1.1.4`_ (Jul 2, 2015)

  * Add support for Python 3 (`issue #6`_).
  * Add support for migrations in Django >= 1.7 (`issue #7`_).
  * Imports which will become deprecated in Django 1.9 are not used now.

* `1.1.3`_ (Oct 11, 2014)

  * ``candv`` dependency updated up to *v1.2.0*.
  * Add support for South (`issue #4`_).
  * Choices' form field can display help text as option's title now
    (`issue #1`_).

* `1.1.0`_ (Jul 19, 2014)

  * rename package to ``choices`` and move into ``candv_x.django``
    (``x`` stands for ``extensions``)

* `1.0.0`_ (Jun 22, 2014)

  Initial version


.. |pypi_package| image:: http://img.shields.io/pypi/v/django-candv-choices.svg?style=flat
   :target: http://badge.fury.io/py/django-candv-choices/
   :alt: Version of PyPI package

.. |pypi_downloads| image:: http://img.shields.io/pypi/dm/django-candv-choices.svg?style=flat
   :target: https://crate.io/packages/django-candv-choices/
   :alt: Number of downloads of PyPI package

.. |python_versions| image:: https://img.shields.io/badge/Python-2.7,3.4-brightgreen.svg?style=flat
   :alt: Supported versions of Python

.. |license| image:: https://img.shields.io/badge/license-LGPLv3-blue.svg?style=flat
   :target: https://github.com/oblalex/django-candv-choices/blob/master/LICENSE
   :alt: Package license

.. |demo_preview| image:: http://i.imgur.com/NXKsgRA.png
   :target: http://django-candv-choices.herokuapp.com/
   :alt: Live demo screenshot

.. _candv: http://candv.readthedocs.org/en/latest/
.. _choices: https://docs.djangoproject.com/en/1.6/ref/models/fields/#django.db.models.Field.choices
.. _Django: https://www.djangoproject.com/
.. _django-rf-candv-choices: https://github.com/oblalex/django-rf-candv-choices

.. _Values: http://candv.readthedocs.org/en/latest/candv.html#candv.Values
.. _VerboseValueConstant: http://candv.readthedocs.org/en/latest/candv.html#candv.VerboseValueConstant

.. _candv usage: http://candv.readthedocs.org/en/latest/usage.html#usage
.. _candv customization: http://candv.readthedocs.org/en/latest/customization.html

.. _hierarchies of constants: http://candv.readthedocs.org/en/latest/usage.html#hierarchies

.. _MultipleChoiceField: https://docs.djangoproject.com/en/1.6/ref/forms/fields/#multiplechoicefield
.. _TypedMultipleChoiceField: https://docs.djangoproject.com/en/1.6/ref/forms/fields/#typedmultiplechoicefield

.. _issue #9: https://github.com/oblalex/django-candv-choices/issues/8
.. _issue #8: https://github.com/oblalex/django-candv-choices/issues/8
.. _issue #7: https://github.com/oblalex/django-candv-choices/issues/7
.. _issue #6: https://github.com/oblalex/django-candv-choices/issues/6
.. _issue #4: https://github.com/oblalex/django-candv-choices/issues/4
.. _issue #1: https://github.com/oblalex/django-candv-choices/issues/1

.. _1.1.5: https://github.com/oblalex/django-candv-choices/compare/v1.1.4...v1.1.5
.. _1.1.4: https://github.com/oblalex/django-candv-choices/compare/v1.1.3...v1.1.4
.. _1.1.3: https://github.com/oblalex/django-candv-choices/compare/v1.1.0...v1.1.3
.. _1.1.0: https://github.com/oblalex/django-candv-choices/compare/v1.0.0...v1.1.0
.. _1.0.0: https://github.com/oblalex/django-candv-choices/releases/tag/v1.0.0
