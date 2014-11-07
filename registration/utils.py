"""
Helper for getting various Python 3 compatibility things without
calculating them over and over.

"""

try:
    from django.utils.six import binary_type
    from django.utils.six import text_type
except ImportError:
    try:
        from six import binary_type
        from six import text_type
    except ImportError:
        # Must be Django < 1.5 on Python 2 if we got here.
        binary_type = str
        text_type = unicode

try:
    from django.contrib.auth import get_user_model
except ImportError:
    from django.contrib.auth.models import User
    get_user_model = lambda: User  # noqa