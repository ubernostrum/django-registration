"""
Error messages, data and custom validation code used in
django-registration's various user-registration form classes.

"""
import re
import unicodedata

from confusable_homoglyphs import confusables
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


CONFUSABLE = _("This name cannot be registered. " "Please choose a different name.")
CONFUSABLE_EMAIL = _(
    "This email address cannot be registered. "
    "Please supply a different email address."
)
DUPLICATE_EMAIL = _(
    "This email address is already in use. " "Please supply a different email address."
)
DUPLICATE_USERNAME = _("A user with that username already exists.")
FREE_EMAIL = _(
    "Registration using free email addresses is prohibited. "
    "Please supply a different email address."
)
RESERVED_NAME = _("This name is reserved and cannot be registered.")
TOS_REQUIRED = _("You must agree to the terms to register")

# WHATWG HTML5 spec, section 4.10.5.1.5.
HTML5_EMAIL_RE = (
    r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]"
    r"+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}"
    r"[a-zA-Z0-9])?(?:\.[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


# Below we construct a large but non-exhaustive list of names which
# users probably should not be able to register with, due to various
# risks:
#
# * For a site which creates email addresses from username, important
#   common addresses must be reserved.
#
# * For a site which creates subdomains from usernames, important
#   common hostnames/domain names must be reserved.
#
# * For a site which uses the username to generate a URL to the user's
#   profile, common well-known filenames must be reserved.
#
# etc., etc.
#
# Credit for basic idea and most of the list to Geoffrey Thomas's blog
# post about names to reserve:
# https://ldpreload.com/blog/names-to-reserve
SPECIAL_HOSTNAMES = [
    # Hostnames with special/reserved meaning.
    "autoconfig",  # Thunderbird autoconfig
    "autodiscover",  # MS Outlook/Exchange autoconfig
    "broadcasthost",  # Network broadcast hostname
    "isatap",  # IPv6 tunnel autodiscovery
    "localdomain",  # Loopback
    "localhost",  # Loopback
    "wpad",  # Proxy autodiscovery
]


PROTOCOL_HOSTNAMES = [
    # Common protocol hostnames.
    "ftp",
    "imap",
    "mail",
    "news",
    "pop",
    "pop3",
    "smtp",
    "usenet",
    "uucp",
    "webmail",
    "www",
]


CA_ADDRESSES = [
    # Email addresses known used by certificate authorities during
    # verification.
    "admin",
    "administrator",
    "hostmaster",
    "info",
    "is",
    "it",
    "mis",
    "postmaster",
    "root",
    "ssladmin",
    "ssladministrator",
    "sslwebmaster",
    "sysadmin",
    "webmaster",
]


RFC_2142 = [
    # RFC-2142-defined names not already covered.
    "abuse",
    "marketing",
    "noc",
    "sales",
    "security",
    "support",
]


NOREPLY_ADDRESSES = [
    # Common no-reply email addresses.
    "mailer-daemon",
    "nobody",
    "noreply",
    "no-reply",
]


SENSITIVE_FILENAMES = [
    # Sensitive filenames.
    "clientaccesspolicy.xml",  # Silverlight cross-domain policy file.
    "crossdomain.xml",  # Flash cross-domain policy file.
    "favicon.ico",
    "humans.txt",
    "keybase.txt",  # Keybase ownership-verification URL.
    "robots.txt",
    ".htaccess",
    ".htpasswd",
]


OTHER_SENSITIVE_NAMES = [
    # Other names which could be problems depending on URL/subdomain
    # structure.
    "account",
    "accounts",
    "auth",
    "authorize",
    "blog",
    "buy",
    "cart",
    "clients",
    "contact",
    "contactus",
    "contact-us",
    "copyright",
    "dashboard",
    "doc",
    "docs",
    "download",
    "downloads",
    "enquiry",
    "faq",
    "help",
    "inquiry",
    "license",
    "login",
    "logout",
    "me",
    "myaccount",
    "oauth",
    "pay",
    "payment",
    "payments",
    "plans",
    "portfolio",
    "preferences",
    "pricing",
    "privacy",
    "profile",
    "register",
    "secure",
    "settings",
    "signin",
    "signup",
    "ssl",
    "status",
    "store",
    "subscribe",
    "terms",
    "tos",
    "user",
    "users",
    "weblog",
    "work",
]


DEFAULT_RESERVED_NAMES = (
    SPECIAL_HOSTNAMES
    + PROTOCOL_HOSTNAMES
    + CA_ADDRESSES
    + RFC_2142
    + NOREPLY_ADDRESSES
    + SENSITIVE_FILENAMES
    + OTHER_SENSITIVE_NAMES
)


@deconstructible
class ReservedNameValidator:
    """
    Validator which disallows many reserved names as form field
    values.

    """

    def __init__(self, reserved_names=DEFAULT_RESERVED_NAMES):
        self.reserved_names = reserved_names

    def __call__(self, value):
        # GH issue 82: this validator only makes sense when the
        # username field is a string type.
        if not isinstance(value, str):
            return
        if value in self.reserved_names or value.startswith(".well-known"):
            raise ValidationError(RESERVED_NAME, code="invalid")

    def __eq__(self, other):
        return self.reserved_names == other.reserved_names


@deconstructible
class CaseInsensitiveUnique:
    """
    Validator which performs a case-insensitive uniqueness check.

    """

    def __init__(self, model, field_name, error_message):
        self.model = model
        self.field_name = field_name
        self.error_message = error_message

    def __call__(self, value):
        # Only run if the username is a string.
        if not isinstance(value, str):
            return
        value = unicodedata.normalize("NFKC", value).casefold()
        if self.model._default_manager.filter(
            **{"{}__iexact".format(self.field_name): value}
        ).exists():
            raise ValidationError(self.error_message, code="unique")

    def __eq__(self, other):
        return (
            self.model == other.model
            and self.field_name == other.field_name
            and self.error_message == other.error_message
        )


@deconstructible
class HTML5EmailValidator(RegexValidator):
    """
    Validator which applies HTML5's email address rules.

    """

    message = EmailValidator.message
    regex = re.compile(HTML5_EMAIL_RE)


def validate_confusables(value):
    """
    Validator which disallows 'dangerous' usernames likely to
    represent homograph attacks.

    A username is 'dangerous' if it is mixed-script (as defined by
    Unicode 'Script' property) and contains one or more characters
    appearing in the Unicode Visually Confusable Characters file.

    """
    if not isinstance(value, str):
        return
    if confusables.is_dangerous(value):
        raise ValidationError(CONFUSABLE, code="invalid")


def validate_confusables_email(value):
    """
    Validator which disallows 'dangerous' email addresses likely to
    represent homograph attacks.

    An email address is 'dangerous' if either the local-part or the
    domain, considered on their own, are mixed-script and contain one
    or more characters appearing in the Unicode Visually Confusable
    Characters file.

    """
    # Email addresses are extremely difficult.
    #
    # The current RFC governing syntax of email addresses is RFC 5322
    # which, as the HTML5 specification succinctly states, "defines a
    # syntax for e-mail addresses that is simultaneously too strict
    # ... too vague ...  and too lax ...  to be of practical use".
    #
    # In order to be useful, this validator must consider only the
    # addr-spec portion of an email address, and must examine the
    # local-part and the domain of that addr-spec
    # separately. Unfortunately, there are no good general-purpose
    # Python libraries currently available (that the author of
    # django-registration is aware of), supported on all versions of
    # Python django-registration supports, which can reliably provide
    # an RFC-complient parse of either a full address or an addr-spec
    # which allows the local-part and domain to be treated separately.
    #
    # To work around this shortcoming, RegistrationForm applies the
    # HTML5 email validation rule, which HTML5 admits (in section
    # 4.10.5.1.5) is a "willful violation" of RFC 5322, to the
    # submitted email address. This will reject many technically-valid
    # but problematic email addresses, including those which make use
    # of comments, or which embed otherwise-illegal characters via
    # quoted-string.
    #
    # That in turn allows this validator to take a much simpler
    # approach: it considers any value containing exactly one '@'
    # (U+0040) to be an addr-spec, and consders everything prior to
    # the '@' to be the local-part and everything after to be the
    # domain, and performs validation on them. Any value not
    # containing exactly one '@' is assumed not to be an addr-spec,
    # and is thus "accepted" by not being validated at all.
    if value.count("@") != 1:
        return
    local_part, domain = value.split("@")
    if confusables.is_dangerous(local_part) or confusables.is_dangerous(domain):
        raise ValidationError(CONFUSABLE_EMAIL, code="invalid")
