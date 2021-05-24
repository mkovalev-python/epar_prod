__author__ = 'Gvammer'
from django.core.mail import EmailMultiAlternatives
from django.core.mail import EmailMessage, BadHeaderError

class PM_MailEvent:
    from_address = 'info@tracker.ru'
    to = ['']
    subject = ''
    message = ''
    plain_content = ''

    event_name = ''
    @staticmethod
    def validateEmail(email):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        try:
            validate_email(email)
            return True
        except ValidationError:
            return False

    def send(self):
        if self.validateEmail(self.to):
            try:
                subject, from_email, to = self.subject, self.from_address, self.to
                text_content = self.plain_content
                html_content = self.message
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            except BadHeaderError:
                return 'Invalid header found.'

        return True
