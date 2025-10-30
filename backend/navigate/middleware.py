"""
Custom middleware for NaviGate application
"""
from django.utils.deprecation import MiddlewareMixin


class DisableCSRFForAPILogin(MiddlewareMixin):
    """
    Middleware to disable CSRF checks for the login API endpoint.

    This is necessary because DRF's SessionAuthentication enforces CSRF
    even when we explicitly set authentication_classes=[] on the view.
    The login endpoint doesn't need CSRF protection since it's a public
    endpoint that creates tokens for subsequent authenticated requests.
    """

    def process_request(self, request):
        if request.path == '/api/auth/login/':
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
