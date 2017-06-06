from django.conf import settings
from django.template.loader import render_to_string, TemplateDoesNotExist


def send_user_activation_email(user, email_ctx,
                               email_subject_template=None,
                               email_body_template=None,
                               email_html_body_template=None):
    """
    Send an activation email to a user.

    """
    # Subject of activation email.
    if not email_subject_template:
        email_subject_template = getattr(
            settings,
            'ACCOUNT_ACTIVATION_EMAIL_SUBJECT_TEMPLATE',
            None
        )

    if not email_subject_template:
        email_subject_template = 'registration/activation_email_subject.txt'

    subject = render_to_string(email_subject_template, email_ctx)

    # Force subject to a single line to avoid header-injection issues.
    subject = ''.join(subject.splitlines())

    # Plain-text body of activation email.
    if not email_body_template:
        email_body_template = getattr(
            settings,
            'ACCOUNT_ACTIVATION_EMAIL_BODY_TEMPLATE',
            None
        )

    if not email_body_template:
        email_body_template = 'registration/activation_email.txt'

    message = render_to_string(email_body_template, email_ctx)

    # HTML alternative of activation email's body.
    if not email_html_body_template:
        email_html_body_template = getattr(
            settings,
            'ACCOUNT_ACTIVATION_EMAIL_HTML_BODY_TEMPLATE',
            None
        )

    if not email_html_body_template:
        email_html_body_template = 'registration/activation_email.html'

    try:
        html_message = render_to_string(email_html_body_template, email_ctx)
    except TemplateDoesNotExist:
        html_message = None

    # Send the rendered activation email.
    user.email_user(subject, message, settings.DEFAULT_FROM_EMAIL,
                    html_message=html_message)
