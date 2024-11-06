"""
Configuration file for the Sphinx documentation builder:

https://www.sphinx-doc.org/

"""

# SPDX-License-Identifier: BSD-3-Clause

import os
import sys
from importlib.metadata import version as get_version

import django
from django.conf import settings

settings.configure(
    INSTALLED_APPS=[
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django_registration",
    ],
    DEBUG=True,
)

django.setup()

extensions = [
    "notfound.extension",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinxext.opengraph",
    "sphinx_copybutton",
    "sphinx_inline_tabs",
]
templates_path = ["_templates"]
source_suffix = {".rst": "restructuredtext"}
master_doc = "index"
project = "django-registration"
copyright = "James Bennett and contributors"
version = get_version("django-registration")
release = version
exclude_trees = ["_build"]
pygments_style = "sphinx"
htmlhelp_basename = "django-registrationdoc"
html_theme = "furo"
latex_documents = [
    (
        "index",
        "django-registration.tex",
        "django-registration Documentation",
        "James Bennett",
        "manual",
    )
]

intersphinx_mapping = {
    "django": (
        "https://docs.djangoproject.com/en/stable/",
        "https://docs.djangoproject.com/en/stable/_objects/",
    ),
    "python": ("https://docs.python.org/3", None),
}

# Spelling check needs an additional module that is not installed by default.
# Add it only if spelling check is requested so docs can be generated without it.
if "spelling" in sys.argv:
    extensions.append("sphinxcontrib.spelling")

# Spelling language.
spelling_lang = "en_US"

# Location of word list.
spelling_word_list_filename = "spelling_wordlist.txt"

# The documentation does not include contributor names, so we skip this because it's
# flaky about needing to scan commit history.
spelling_ignore_contributor_names = False

# OGP metadata configuration.
ogp_enable_meta_description = True
ogp_site_url = "https://django-registration.readthedocs.io/"

# Django settings for sphinxcontrib-django.
sys.path.insert(0, os.path.abspath("."))
django_settings = "docs_settings"
