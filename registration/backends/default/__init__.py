"""
Backwards-compatible import location for the model-based activation
workflow.

Formerly this was the default registration workflow of
django-registration, and so was found at
registration.backends.default. As of the current release, however, it
is no longer the default workflow (there is now no default), and has
accordingly been moved to registration.backends.model_activation.

Attempting to import the views or include() the URLconf found here
will raise deprecation warnings to make users aware of this fact, and
remind them to modify imports and include()s, as support for this
location will be removed in django-registration 3.0

"""
