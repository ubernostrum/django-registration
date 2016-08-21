"""
Error messages, data and custom validation code used in
django-registration's various user-registration form classes.

"""

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


DUPLICATE_EMAIL = _(u"This email address is already in use. "
                    u"Please supply a different email address.")
FREE_EMAIL = _(u"Registration using free email addresses is prohibited. "
               u"Please supply a different email address.")
RESERVED_NAME = _(u"This value is reserved and cannot be registered.")
TOS_REQUIRED = _(u"You must agree to the terms to register")


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
    'autoconfig',     # Thunderbird autoconfig
    'autodiscover',   # MS Outlook/Exchange autoconfig
    'broadcasthost',  # Network broadcast hostname
    'isatap',         # IPv6 tunnel autodiscovery
    'localdomain',    # Loopback
    'localhost',      # Loopback
    'wpad',           # Proxy autodiscovery
]


PROTOCOL_HOSTNAMES = [
    # Common protocol hostnames.
    'ftp',
    'imap',
    'mail',
    'news',
    'pop',
    'pop3',
    'smtp',
    'usenet',
    'uucp',
    'webmail',
    'www',
]


CA_ADDRESSES = [
    # Email addresses known used by certificate authorities during
    # verification.
    'admin',
    'administrator',
    'hostmaster',
    'info',
    'is',
    'it',
    'mis',
    'postmaster',
    'root',
    'ssladmin',
    'ssladministrator',
    'sslwebmaster',
    'sysadmin',
    'webmaster',
]


RFC_2142 = [
    # RFC-2142-defined names not already covered.
    'abuse',
    'marketing',
    'noc',
    'sales',
    'security',
    'support',
]


NOREPLY_ADDRESSES = [
    # Common no-reply email addresses.
    'mailer-daemon',
    'nobody',
    'noreply',
    'no-reply',
]


SENSITIVE_FILENAMES = [
    # Sensitive filenames.
    'clientaccesspolicy.xml',  # Silverlight cross-domain policy file.
    'crossdomain.xml',         # Flash cross-domain policy file.
    'favicon.ico',
    'humans.txt',
    'robots.txt',
    '.htaccess',
    '.htpasswd',
]


OTHER_SENSITIVE_NAMES = [
    # Other names which could be problems depending on URL/subdomain
    # structure.
    'account',
    'accounts',
    'blog',
    'buy',
    'clients',
    'contact',
    'contactus',
    'contact-us',
    'copyright',
    'dashboard',
    'doc',
    'docs',
    'download',
    'downloads',
    'enquiry',
    'faq',
    'help',
    'inquiry',
    'license',
    'login',
    'logout',
    'me',
    'myaccount',
    'payments',
    'plans',
    'portfolio',
    'preferences',
    'pricing',
    'privacy',
    'profile',
    'register'
    'secure',
    'settings',
    'signin',
    'signup',
    'ssl',
    'status',
    'subscribe',
    'terms',
    'tos',
    'user',
    'users'
    'weblog',
    'work',
]


DEFAULT_RESERVED_NAMES = (SPECIAL_HOSTNAMES + PROTOCOL_HOSTNAMES +
                          CA_ADDRESSES + RFC_2142 + NOREPLY_ADDRESSES +
                          SENSITIVE_FILENAMES + OTHER_SENSITIVE_NAMES)


class ReservedNameValidator(object):
    """
    Validator which disallows many reserved names as form field
    values.

    """
    def __init__(self, reserved_names=DEFAULT_RESERVED_NAMES):
        self.reserved_names = reserved_names

    def __call__(self, value):
        if value in self.reserved_names or \
           value.startswith('.well-known'):
            raise ValidationError(
                RESERVED_NAME, code='invalid'
            )
