import ssl
import smtplib
from django.core.mail.backends.smtp import EmailBackend

original_open = EmailBackend.open

def patched_open(self):
    self.connection = smtplib.SMTP(self.host, self.port, timeout=self.timeout)
    self.connection.ehlo()
    context = ssl._create_unverified_context()  # <<< disables SSL verification
    self.connection.starttls(context=context)
    self.connection.ehlo()
    if self.username and self.password:
        self.connection.login(self.username, self.password)

EmailBackend.open = patched_open
