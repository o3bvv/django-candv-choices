# -*- coding: utf-8 -*-
"""
Adds support for custom complex choices for Django models.
"""

# Import 'ChoicesFieldListFilter' to invoke registration of filter
from .admin import ChoicesFieldListFilter
from .db import ChoicesField
