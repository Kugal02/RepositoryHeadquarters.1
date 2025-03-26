# agency/email_backend.py
import ssl
import certifi
from django.core.mail.backends.smtp import EmailBackend

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inject trusted CA bundle for SSL validation
        self.ssl_certfile = certifi.where()

    @property
    def ssl_context(self):
        context = ssl.create_default_context(cafile=self.ssl_certfile)
        if self.ssl_keyfile and self.ssl_certfile:
            context.load_cert_chain(certfile=self.ssl_certfile, keyfile=self.ssl_keyfile)
        return context
