from django.utils import timezone
import pytz


class TimezoneMiddleware:
    """Middleware to set timezone based on user preferences"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Set timezone to Asia/Riyadh as default
        # Can be customized per user if needed
        timezone.activate(pytz.timezone('Asia/Riyadh'))
        response = self.get_response(request)
        return response


class AutoProgressOrdersMiddleware:
    """Middleware to auto-progress orders based on status"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Placeholder for auto-progress logic
        # This can be expanded to automatically update order statuses
        response = self.get_response(request)
        return response
