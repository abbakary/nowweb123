from django.utils import timezone
from .models import Notification, CompanyProfile


def header_notifications(request):
    """Add notifications to template context for authenticated users"""
    notifications = []
    unread_count = 0

    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    return {
        'notifications': notifications,
        'unread_notifications_count': unread_count,
    }


def company_profile(request):
    """Add company profile to template context for all requests"""
    try:
        profile = CompanyProfile.get_profile()
    except:
        profile = None

    return {
        'company': profile,
    }
