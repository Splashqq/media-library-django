import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string

logger = logging.getLogger(__name__)


class Mailer:
    @staticmethod
    def _render_template(template_name, **kwargs):
        text_content = render_to_string(
            template_name,
            context=kwargs,
        )
        template = get_template(template_name)
        html_content = template.render(kwargs)
        return text_content, html_content

    @classmethod
    def _send_mail(cls, subject, text_content, html_content, to):
        message = EmailMultiAlternatives(
            subject=subject, body=text_content, from_email=None, to=to
        )
        message.mixed_subtype = "related"
        message.attach_alternative(html_content, "text/html")

        message.send(fail_silently=False)

    def send_password_reset_message(self, to, url, email, password):
        text, html = self._render_template(
            "password_reset_email.html", url=url, email=email, password=password
        )
        try:
            self._send_mail("Password reset message", text, html, [to])
        except Exception as e:
            logger.error(f"Failed to send email: {type(e)} {e}")
