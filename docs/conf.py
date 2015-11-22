import os


on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

extensions = []
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
project = u'django-registration'
copyright = u'2007-2015, James Bennett'
version = '2.0'
release = '2.0.3'
exclude_trees = ['_build']
pygments_style = 'sphinx'
html_static_path = ['_static']
htmlhelp_basename = 'django-registrationdoc'
latex_documents = [
    ('index', 'django-registration.tex', u'django-registration Documentation',
     u'James Bennett', 'manual'),
]
if not on_rtd:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
