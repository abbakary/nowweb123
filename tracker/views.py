from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
import json

from .models import (
    Customer, UserProfile, ResearchService, ConsultancySubService,
    ServiceRequest, Workshop, WorkshopRegistration, ClientTestimonial
)
from .forms import (
    CustomUserCreationForm, CustomUserLoginForm, CustomPasswordChangeForm,
    CustomerProfileForm, UserProfileForm, ServiceRequestForm,
    ContactForm
)


# ============================================================================
# AUTHENTICATION VIEWS
# ============================================================================

@require_http_methods(["GET", "POST"])
def user_register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            phone = form.cleaned_data.get('phone', '')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')

            # Create customer profile with phone
            Customer.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': email.split('@')[0],
                    'phone': phone,
                    'user': user
                }
            )

            # Create user profile
            UserProfile.objects.get_or_create(user=user)

            # Auto-login the user after registration
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('home')
            else:
                messages.success(request, 'Account created successfully! Please log in.')
                return redirect('login')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    context = {'form': form}
    return render(request, 'register.html', context)


@require_http_methods(["GET", "POST"])
def user_login(request):
    """User login view - email based with proper role-based redirects"""
    if request.user.is_authenticated:
        # Redirect authenticated users based on their role
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')

            user = None
            if identifier and '@' in identifier:
                try:
                    matched_user = User.objects.get(email__iexact=identifier)
                    user = authenticate(request, username=matched_user.username, password=password)
                except User.DoesNotExist:
                    user = authenticate(request, username=identifier, password=password)
            else:
                user = authenticate(request, username=identifier, password=password)

            if user is not None:
                login(request, user)

                # Set session timeout based on remember_me
                if remember_me:
                    request.session.set_expiry(1209600)  # 2 weeks
                else:
                    request.session.set_expiry(0)  # Session expires on browser close

                # Role-based redirect
                if user.is_staff:
                    messages.success(request, f'Welcome back, Admin {user.first_name or user.email}!')
                    return redirect('admin_dashboard')
                else:
                    user_name = user.get_full_name() or user.email.split('@')[0]
                    messages.success(request, f'Welcome back, {user_name}!')
                    # Redirect to next page or user home
                    next_page = request.GET.get('next', 'home')
                    return redirect(next_page)
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
    else:
        form = CustomUserLoginForm()

    context = {'form': form}
    return render(request, 'login.html', context)

@require_http_methods(["GET", "POST"])
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    next_page = request.GET.get('next') or request.POST.get('next') or settings.LOGOUT_REDIRECT_URL or 'home'
    return redirect(next_page)


# =========================================================================
# USER PROFILE VIEWS
# ============================================================================

@login_required
def user_profile(request):
    """View user profile"""
    user = request.user

    # Get or create customer
    customer, _ = Customer.objects.get_or_create(
        email=user.email,
        defaults={
            'full_name': user.get_full_name() or user.email.split('@')[0],
            'phone': '',
            'user': user,
        }
    )

    # Get or create user profile
    user_profile, _ = UserProfile.objects.get_or_create(user=user)

    # Get user statistics
    service_requests = ServiceRequest.objects.filter(customer=customer)
    completed_requests = service_requests.filter(status='completed').count()
    pending_requests = service_requests.filter(status='pending').count()
    workshop_registrations = WorkshopRegistration.objects.filter(customer=customer)

    context = {
        'customer': customer,
        'user_profile': user_profile,
        'completed_requests': completed_requests,
        'pending_requests': pending_requests,
        'total_requests': service_requests.count(),
        'workshop_count': workshop_registrations.count(),
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile"""
    user = request.user

    # Get or create customer
    customer, _ = Customer.objects.get_or_create(
        email=user.email,
        defaults={
            'full_name': user.get_full_name() or user.email.split('@')[0],
            'phone': '',
            'user': user,
        }
    )

    # Get or create user profile
    user_profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        customer_form = CustomerProfileForm(request.POST, instance=customer)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if customer_form.is_valid() and user_profile_form.is_valid():
            customer_form.save()
            user_profile_form.save()
            
            # Update user's name
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')
    else:
        customer_form = CustomerProfileForm(instance=customer)
        user_profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'customer_form': customer_form,
        'user_profile_form': user_profile_form,
        'customer': customer,
        'user_profile': user_profile,
    }
    return render(request, 'edit_profile.html', context)


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Update session to avoid logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('user_profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    context = {'form': form}
    return render(request, 'change_password.html', context)


@login_required
def user_settings(request):
    """User account settings"""
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Handle various settings updates
        action = request.POST.get('action')
        
        if action == 'newsletter':
            user_profile.newsletter_subscribed = 'newsletter' in request.POST
            user_profile.save()
            messages.success(request, 'Newsletter preference updated!')
        
        return redirect('user_settings')
    
    context = {'user_profile': user_profile}
    return render(request, 'user_settings.html', context)


# ============================================================================
# API ENDPOINTS (JSON RESPONSES)
# ============================================================================

@require_http_methods(["POST"])
@csrf_exempt
def check_username_availability(request):
    """Check if username is available (AJAX)"""
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        
        if not username or len(username) < 3:
            return JsonResponse({
                'available': False,
                'message': 'Username must be at least 3 characters'
            })
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'available': False,
                'message': 'This username is already taken'
            })
        
        return JsonResponse({
            'available': True,
            'message': 'Username is available'
        })
    except Exception as e:
        return JsonResponse({
            'available': False,
            'message': f'Error: {str(e)}'
        }, status=400)


@require_http_methods(["POST"])
@csrf_exempt
def check_email_availability(request):
    """Check if email is available (AJAX)"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        
        if not email or '@' not in email:
            return JsonResponse({
                'available': False,
                'message': 'Please enter a valid email'
            })
        
        if User.objects.filter(email=email).exists() or Customer.objects.filter(email=email).exists():
            return JsonResponse({
                'available': False,
                'message': 'This email is already registered'
            })
        
        return JsonResponse({
            'available': True,
            'message': 'Email is available'
        })
    except Exception as e:
        return JsonResponse({
            'available': False,
            'message': f'Error: {str(e)}'
        }, status=400)


@require_http_methods(["GET"])
def get_services_json(request):
    """Get services list as JSON"""
    category = request.GET.get('category')
    services = ResearchService.objects.filter(is_active=True)
    
    if category:
        services = services.filter(category=category)
    
    services_list = [
        {
            'id': service.id,
            'name': service.name,
            'category': service.category,
            'description': service.description,
            'icon': service.icon,
            'price_from': str(service.price_from) if service.price_from else None,
            'price_to': str(service.price_to) if service.price_to else None,
            'turnaround_time': service.turnaround_time,
        }
        for service in services
    ]
    
    return JsonResponse({'services': services_list})


@require_http_methods(["GET"])
def get_testimonials_json(request):
    """Get testimonials as JSON"""
    testimonials = ClientTestimonial.objects.filter(
        is_published=True
    ).select_related('customer', 'service').order_by('-created_at')[:10]
    
    testimonials_list = [
        {
            'id': t.id,
            'customer_name': t.customer.full_name,
            'rating': t.rating,
            'quote': t.quote,
            'service': t.service.name if t.service else None,
        }
        for t in testimonials
    ]
    
    return JsonResponse({'testimonials': testimonials_list})


@require_http_methods(["GET"])
def get_workshops_json(request):
    """Get upcoming workshops as JSON"""
    workshops = Workshop.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).order_by('date')[:10]
    
    workshops_list = [
        {
            'id': w.id,
            'title': w.title,
            'date': w.date.isoformat(),
            'location': w.location,
            'is_online': w.is_online,
            'price': str(w.price) if w.price else '0',
            'registered_count': w.get_registration_count(),
            'is_full': w.is_full(),
        }
        for w in workshops
    ]
    
    return JsonResponse({'workshops': workshops_list})


@require_http_methods(["POST"])
@csrf_exempt
def submit_contact_ajax(request):
    """Submit contact form via AJAX"""
    try:
        data = json.loads(request.body)
        
        form = ContactForm(data)
        if form.is_valid():
            # Create service request
            customer, _ = Customer.objects.get_or_create(
                email=form.cleaned_data['email'],
                defaults={
                    'full_name': form.cleaned_data['full_name'],
                    'phone': form.cleaned_data.get('phone', '')
                }
            )
            
            service_id = form.cleaned_data.get('service')
            service = None
            if service_id:
                try:
                    service = ResearchService.objects.get(id=service_id)
                except ResearchService.DoesNotExist:
                    pass
            
            ServiceRequest.objects.create(
                customer=customer,
                service=service,
                title=form.cleaned_data['subject'],
                description=form.cleaned_data['message'],
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you! We will get back to you soon.'
            })
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = error_list[0]
            
            return JsonResponse({
                'success': False,
                'errors': errors,
                'message': 'Please correct the errors below'
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)
