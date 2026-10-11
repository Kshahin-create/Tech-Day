import ssl
from django.core.mail.backends.smtp import EmailBackend

try:
    import certifi
except ImportError:
    certifi = None

class CustomEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False
        
        try:
            if certifi:
                self.ssl_context = ssl.create_default_context(cafile=certifi.where())
            else:
                self.ssl_context = ssl.create_default_context()
            
            return super().open()
        except Exception:
            if not self.fail_silently:
                raise
            return False
