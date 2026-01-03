from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from .models import (
    ResearchService, ConsultancySubService, ServiceRequest, ClientTestimonial,
    Workshop, WorkshopRegistration, Customer, ZoomAppointment, ServiceImage,
    TutorialVideo, ServiceFAQ
)


def _auto_generate_testimonials():
    """Auto-generate testimonials from completed service requests"""
    completed_requests = ServiceRequest.objects.filter(
        status='completed'
    ).select_related('customer', 'service')

    for request_obj in completed_requests:
        testimonial_exists = ClientTestimonial.objects.filter(
            customer=request_obj.customer,
            service=request_obj.service
        ).exists()

        if not testimonial_exists and request_obj.customer and request_obj.service:
            default_quotes = [
                f"Excellent service! The {request_obj.service.name} was completed professionally and on time.",
                f"Very satisfied with the {request_obj.service.name} work. Highly recommended!",
                f"Great experience with {request_obj.service.name}. Will definitely use again.",
                f"Outstanding quality for {request_obj.service.name}. Team was very responsive.",
                f"Impressive results from the {request_obj.service.name}. Worth every penny!"
            ]

            import random
            quote = random.choice(default_quotes)

            ClientTestimonial.objects.create(
                customer=request_obj.customer,
                service=request_obj.service,
                rating=5,
                quote=quote,
                is_published=True,
                is_featured=False
            )


def home(request):
    """Home page with featured services and testimonials"""
    featured_services = ResearchService.objects.filter(
        is_active=True,
        category__in=['concept_proposal', 'thesis', 'articles']
    ).order_by('display_order')[:6]

    # Auto-generate testimonials from completed service requests
    _auto_generate_testimonials()

    testimonials = ClientTestimonial.objects.filter(
        is_published=True
    ).order_by('-created_at')[:6]

    context = {
        'featured_services': featured_services,
        'testimonials': testimonials,
    }
    return render(request, 'home.html', context)


def services(request):
    """Services listing page"""
    # Default placeholder images for services
    default_images = {
        'concept_proposal': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&h=400&fit=crop',
        'thesis': 'https://images.unsplash.com/photo-1507842217343-583f20270319?w=600&h=400&fit=crop',
        'articles': 'https://images.unsplash.com/photo-1455390883262-7f6f25510923?w=600&h=400&fit=crop',
        'data_analysis': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop',
        'research_design': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop',
        'training_capacity': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&h=400&fit=crop',
        'default': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=600&h=400&fit=crop',
    }

    # Separate Academic Writing Services and Training & Capacity Building
    academic_services = ResearchService.objects.filter(
        is_active=True
    ).exclude(category__in=['consultancy', 'training_capacity']).prefetch_related(
        'images', 'tutorial_videos', 'faqs'
    ).order_by('display_order')

    training_services = ResearchService.objects.filter(
        is_active=True,
        category='training_capacity'
    ).prefetch_related(
        'images', 'tutorial_videos', 'faqs'
    ).order_by('display_order')

    consultancy_services = ConsultancySubService.objects.filter(
        is_active=True
    ).order_by('display_order')

    workshops = Workshop.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).order_by('date')[:6]

    # Get FAQs that are published
    all_services_list = list(academic_services) + list(training_services)
    service_faqs = {}
    for service in all_services_list:
        service_faqs[service.id] = service.faqs.filter(is_published=True).order_by('display_order')

    # Get published tutorial videos
    service_videos = {}
    for service in all_services_list:
        service_videos[service.id] = service.tutorial_videos.filter(is_published=True).order_by('display_order')

    # Get featured images with fallbacks
    service_images = {}
    service_image_urls = {}
    for service in all_services_list:
        featured = service.images.filter(is_featured=True).first()
        service_images[service.id] = featured

        # Set image URL with fallback
        if featured:
            service_image_urls[service.id] = featured.image.url
        else:
            # Use default image based on category
            service_image_urls[service.id] = default_images.get(service.category, default_images['default'])

    context = {
        'research_services': academic_services,
        'training_services': training_services,
        'consultancy_services': consultancy_services,
        'workshops': workshops,
        'service_faqs': service_faqs,
        'service_videos': service_videos,
        'service_images': service_images,
        'service_image_urls': service_image_urls,
    }
    return render(request, 'services.html', context)


def service_detail(request, pk):
    """Service detail page"""
    # Default placeholder images for services
    default_images = {
        'concept_proposal': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&h=400&fit=crop',
        'thesis': 'https://images.unsplash.com/photo-1507842217343-583f20270319?w=600&h=400&fit=crop',
        'articles': 'https://images.unsplash.com/photo-1455390883262-7f6f25510923?w=600&h=400&fit=crop',
        'data_analysis': 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&h=400&fit=crop',
        'research_design': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&h=400&fit=crop',
        'training_capacity': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=600&h=400&fit=crop',
        'default': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=600&h=400&fit=crop',
    }

    service = get_object_or_404(ResearchService, pk=pk, is_active=True)

    _auto_generate_testimonials()

    # Get related services
    related_services = ResearchService.objects.filter(
        is_active=True,
        category=service.category
    ).exclude(id=service.id).order_by('display_order')[:2]

    # Get testimonials for this service
    testimonials = ClientTestimonial.objects.filter(
        service=service,
        is_published=True
    ).order_by('-created_at')[:4]

    # Get service images
    featured_image = service.images.filter(is_featured=True).first()
    all_images = service.images.all().order_by('display_order')

    # Get featured image URL with fallback
    featured_image_url = featured_image.image.url if featured_image else default_images.get(service.category, default_images['default'])

    # Get tutorial videos
    tutorial_videos = service.tutorial_videos.filter(is_published=True).order_by('display_order')

    # Get FAQs
    faqs = service.faqs.filter(is_published=True).order_by('display_order')

    context = {
        'service': service,
        'related_services': related_services,
        'testimonials': testimonials,
        'featured_image': featured_image,
        'featured_image_url': featured_image_url,
        'all_images': all_images,
        'tutorial_videos': tutorial_videos,
        'faqs': faqs,
    }
    return render(request, 'service_detail.html', context)


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        service_id = request.POST.get('service', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if not all([full_name, email, subject, message]):
            messages.error(request, 'Please fill in all required fields.')
            return redirect('contact')
        
        try:
            # Find or create customer
            customer, _ = Customer.objects.get_or_create(
                full_name=full_name,
                phone=phone or '',
                defaults={'email': email}
            )
            
            # Create service request
            service_req = ServiceRequest.objects.create(
                customer=customer,
                title=subject,
                description=message,
                status='pending'
            )
            
            if service_id:
                try:
                    service = ResearchService.objects.get(id=service_id)
                    service_req.service = service
                    service_req.save()
                except ResearchService.DoesNotExist:
                    pass
            
            messages.success(request, 'Thank you! We\'ll get back to you soon.')
            return redirect('home')
        except Exception as e:
            messages.error(request, f'Error submitting contact form: {str(e)}')
            return redirect('contact')
    
    services = ResearchService.objects.filter(is_active=True).order_by('name')
    context = {'services': services}
    return render(request, 'contact.html', context)


def about(request):
    """About page"""
    from .models import Leadership

    services_count = ResearchService.objects.filter(is_active=True).count()
    consultancy_count = ConsultancySubService.objects.filter(is_active=True).count()
    clients_count = Customer.objects.count()
    completed_count = ServiceRequest.objects.filter(status='completed').count()
    leadership_members = Leadership.objects.filter(is_active=True).order_by('display_order')

    context = {
        'services_count': services_count,
        'consultancy_count': consultancy_count,
        'clients_count': clients_count,
        'completed_count': completed_count,
        'leadership_members': leadership_members,
    }
    return render(request, 'about.html', context)


def service_request(request, pk):
    """Service request form (client initiates service request)"""
    service = get_object_or_404(ResearchService, pk=pk, is_active=True)

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to request a service.')
            return redirect('login')

        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        deadline = request.POST.get('deadline', '')
        budget = request.POST.get('budget', '')

        if not title or not description:
            messages.error(request, 'Please provide a title and description.')
            return redirect('service_detail', pk=service.id)

        try:
            # Get or create customer by email
            customer, _ = Customer.objects.get_or_create(
                email=request.user.email,
                defaults={'full_name': request.user.get_full_name() or request.user.username, 'phone': ''}
            )

            service_req = ServiceRequest.objects.create(
                customer=customer,
                service=service,
                title=title,
                description=description,
                deadline=deadline or None,
                budget=budget or None,
                status='pending'
            )
            messages.success(request, 'Service request submitted successfully!')
            return redirect('client_dashboard')
        except Exception as e:
            messages.error(request, f'Error submitting request: {str(e)}')
            return redirect('service_detail', pk=service.id)

    context = {'service': service}
    return render(request, 'service_request.html', context)


def workshop_detail(request, pk):
    """Workshop detail and registration"""
    workshop = get_object_or_404(Workshop, pk=pk, is_active=True)

    is_registered = False
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(email=request.user.email)
            is_registered = WorkshopRegistration.objects.filter(
                workshop=workshop,
                customer=customer
            ).exists()
        except Customer.DoesNotExist:
            pass

    # Get Zoom appointment if workshop is online
    zoom_appointment = None
    if workshop.is_online:
        try:
            zoom_appointment = ZoomAppointment.objects.get(workshop=workshop, is_active=True)
        except ZoomAppointment.DoesNotExist:
            pass

    context = {
        'workshop': workshop,
        'is_registered': is_registered,
        'zoom_appointment': zoom_appointment,
    }
    return render(request, 'workshop_detail.html', context)


@login_required
def register_workshop(request, pk):
    """Register for a workshop"""
    workshop = get_object_or_404(Workshop, pk=pk, is_active=True)

    try:
        # Get or create customer by email
        customer, _ = Customer.objects.get_or_create(
            email=request.user.email,
            defaults={'full_name': request.user.get_full_name() or request.user.username, 'phone': ''}
        )

        # Check if already registered
        registration, created = WorkshopRegistration.objects.get_or_create(
            workshop=workshop,
            customer=customer,
            defaults={'status': 'registered'}
        )

        if created:
            messages.success(request, 'Successfully registered for the workshop!')
        else:
            messages.info(request, 'You are already registered for this workshop.')

        return redirect('workshop_detail', pk=workshop.id)
    except Exception as e:
        messages.error(request, f'Error registering for workshop: {str(e)}')
        return redirect('workshop_detail', pk=workshop.id)


@login_required
def client_dashboard(request):
    """Client dashboard with their service requests"""
    # Get or create customer profile
    customer, created = Customer.objects.get_or_create(
        email=request.user.email,
        defaults={
            'full_name': request.user.get_full_name() or request.user.email.split('@')[0],
            'phone': '',
            'user': request.user,
        }
    )

    # If customer was just created, redirect to profile to complete setup
    if created:
        messages.info(request, 'Welcome! Please complete your profile.')
        return redirect('user_profile')

    service_requests = ServiceRequest.objects.filter(customer=customer).order_by('-created_at')
    workshop_registrations = WorkshopRegistration.objects.filter(customer=customer).order_by('-registered_at')

    context = {
        'service_requests': service_requests,
        'workshop_registrations': workshop_registrations,
        'customer': customer,
    }
    return render(request, 'client_dashboard.html', context)


# Admin Views
@login_required
def admin_dashboard(request):
    """Main admin dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    total_clients = Customer.objects.count()
    pending_requests = ServiceRequest.objects.filter(status='pending').count()
    completed_this_month = ServiceRequest.objects.filter(
        status='completed',
        completed_at__month=timezone.now().month,
        completed_at__year=timezone.now().year
    ).count()
    upcoming_workshops = Workshop.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).count()
    
    recent_requests = ServiceRequest.objects.all().order_by('-created_at')[:5]
    upcoming_workshops_list = Workshop.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).order_by('date')[:5]
    
    context = {
        'total_clients': total_clients,
        'pending_requests': pending_requests,
        'completed_this_month': completed_this_month,
        'upcoming_workshops': upcoming_workshops,
        'recent_requests': recent_requests,
        'upcoming_workshops_list': upcoming_workshops_list,
    }
    return render(request, 'admin_dashboard.html', context)


@login_required
def admin_overview(request):
    """Admin overview/analytics"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    # Get dashboard statistics
    total_clients = Customer.objects.count()
    pending_requests = ServiceRequest.objects.filter(status='pending').count()
    completed_this_month = ServiceRequest.objects.filter(
        status='completed',
        completed_at__month=timezone.now().month,
        completed_at__year=timezone.now().year
    ).count()
    upcoming_workshops = Workshop.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).count()

    # Recent requests
    recent_requests = ServiceRequest.objects.all().order_by('-created_at')[:5]

    # Upcoming workshops
    upcoming_workshops_list = Workshop.objects.filter(
        is_active=True,
        date__gte=timezone.now()
    ).order_by('date')[:5]

    context = {
        'total_clients': total_clients,
        'pending_requests': pending_requests,
        'completed_this_month': completed_this_month,
        'upcoming_workshops': upcoming_workshops,
        'recent_requests': recent_requests,
        'upcoming_workshops_list': upcoming_workshops_list,
    }
    return render(request, 'admin/overview.html', context)


@login_required
def admin_services(request):
    """Admin services management"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    services = ResearchService.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('name', '').strip()
            category = request.POST.get('category', '').strip()
            description = request.POST.get('description', '').strip()

            if name and category and description:
                ResearchService.objects.create(
                    name=name,
                    category=category,
                    description=description,
                    price_from=request.POST.get('price_from') or None,
                    price_to=request.POST.get('price_to') or None,
                    turnaround_time=request.POST.get('turnaround_time'),
                    is_active=True
                )
                messages.success(request, 'Service created successfully!')
            else:
                messages.error(request, 'Please fill in all required fields.')
        elif action == 'delete':
            try:
                service_id = request.POST.get('service_id')
                service = ResearchService.objects.get(id=service_id)
                service_name = service.name
                service.delete()
                messages.success(request, f'Service "{service_name}" deleted successfully.')
            except ResearchService.DoesNotExist:
                messages.error(request, 'Service not found.')

        return redirect('admin_services')
    
    active_services = services.filter(is_active=True).count()
    total_requests = ServiceRequest.objects.count()

    context = {
        'services': services,
        'active_services': active_services,
        'total_requests': total_requests,
    }
    return render(request, 'admin/services.html', context)


@login_required
def admin_consultancy(request):
    """Admin consultancy management"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    consultancy_services = ConsultancySubService.objects.all().order_by('display_order', '-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            consultancy_type = request.POST.get('consultancy_type', '').strip()
            description = request.POST.get('description', '').strip()

            if name and consultancy_type and description:
                ConsultancySubService.objects.create(
                    name=name,
                    consultancy_type=consultancy_type,
                    description=description,
                    features=request.POST.get('features', '').strip(),
                    icon=request.POST.get('icon', 'ri-discuss-line').strip(),
                    hourly_rate=request.POST.get('hourly_rate') or None,
                    is_active=True
                )
                messages.success(request, 'Consultancy service created successfully!')
            else:
                messages.error(request, 'Please fill in all required fields.')
        elif action == 'update':
            try:
                service_id = request.POST.get('service_id')
                service = ConsultancySubService.objects.get(id=service_id)

                service.name = request.POST.get('name', service.name).strip()
                service.consultancy_type = request.POST.get('consultancy_type', service.consultancy_type).strip()
                service.description = request.POST.get('description', service.description).strip()
                service.features = request.POST.get('features', '').strip()
                service.icon = request.POST.get('icon', 'ri-discuss-line').strip()
                service.hourly_rate = request.POST.get('hourly_rate') or None
                service.save()

                messages.success(request, f'Consultancy service "{service.name}" updated successfully!')
            except ConsultancySubService.DoesNotExist:
                messages.error(request, 'Service not found.')
        elif action == 'delete':
            try:
                service_id = request.POST.get('service_id')
                service = ConsultancySubService.objects.get(id=service_id)
                service_name = service.name
                service.delete()
                messages.success(request, f'Consultancy service "{service_name}" deleted successfully.')
            except ConsultancySubService.DoesNotExist:
                messages.error(request, 'Service not found.')

        return redirect('admin_consultancy')

    context = {'consultancy_services': consultancy_services}
    return render(request, 'admin/consultancy_enhanced.html', context)


@login_required
def admin_clients(request):
    """Admin clients management"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    if request.method == 'POST':
        action = request.POST.get('action')
        customer_id = request.POST.get('customer_id')

        try:
            customer = Customer.objects.get(id=customer_id)

            if action == 'edit':
                customer.full_name = request.POST.get('full_name', customer.full_name)
                customer.phone = request.POST.get('phone', customer.phone)
                customer.organization = request.POST.get('organization', customer.organization)
                customer.customer_type = request.POST.get('customer_type', customer.customer_type)
                customer.save()
                messages.success(request, f'Customer {customer.full_name} updated successfully.')
            elif action == 'toggle_status':
                customer.is_active = not customer.is_active
                customer.save()
                status_text = 'activated' if customer.is_active else 'deactivated'
                messages.success(request, f'Customer {status_text}.')
            elif action == 'view':
                messages.info(request, f'Viewing details for {customer.full_name}')
        except Customer.DoesNotExist:
            messages.error(request, 'Customer not found.')

        return redirect('admin_clients')

    customers = Customer.objects.all().order_by('-registration_date')
    new_this_month = Customer.objects.filter(
        registration_date__month=timezone.now().month,
        registration_date__year=timezone.now().year
    ).count()
    organization_count = Customer.objects.filter(customer_type='organization').count()
    verified_count = Customer.objects.filter(is_active=True).count()

    context = {
        'customers': customers,
        'new_this_month': new_this_month,
        'organization_count': organization_count,
        'verified_count': verified_count,
    }
    return render(request, 'admin/clients.html', context)


@login_required
def admin_requests(request):
    """Admin service requests management"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    service_requests = ServiceRequest.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        request_id = request.POST.get('request_id')
        
        try:
            service_req = ServiceRequest.objects.get(id=request_id)
            
            if action == 'accept':
                service_req.status = 'accepted'
                service_req.save()
                messages.success(request, 'Service request accepted.')
            elif action == 'complete':
                service_req.status = 'completed'
                service_req.completed_at = timezone.now()
                service_req.save()
                messages.success(request, 'Service request completed.')
            elif action == 'cancel':
                service_req.status = 'cancelled'
                service_req.save()
                messages.success(request, 'Service request cancelled.')
        except ServiceRequest.DoesNotExist:
            messages.error(request, 'Service request not found.')
        
        return redirect('admin_requests')
    
    context = {'service_requests': service_requests}
    return render(request, 'admin/requests.html', context)


@login_required
def admin_workshops(request):
    """Admin workshops management"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    workshops = Workshop.objects.all().order_by('-date')

    if request.method == 'POST':
        action = request.POST.get('action')
        workshop_id = request.POST.get('workshop_id')

        if action == 'delete':
            try:
                workshop = Workshop.objects.get(id=workshop_id)
                workshop_title = workshop.title
                workshop.delete()
                messages.success(request, f'Workshop "{workshop_title}" deleted successfully.')
            except Workshop.DoesNotExist:
                messages.error(request, 'Workshop not found.')
            return redirect('admin_workshops')

        if action == 'create':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            date_str = request.POST.get('date')

            if title and description and date_str:
                try:
                    Workshop.objects.create(
                        title=title,
                        description=description,
                        date=date_str,
                        is_online=request.POST.get('is_online') == 'True',
                        location=request.POST.get('location'),
                        max_participants=request.POST.get('max_participants') or None,
                        price=request.POST.get('price') or 0,
                        is_active=True
                    )
                    messages.success(request, 'Workshop created successfully!')
                except Exception as e:
                    messages.error(request, f'Error creating workshop: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields.')

        return redirect('admin_workshops')
    
    context = {'workshops': workshops}
    return render(request, 'admin/workshops.html', context)


@login_required
def admin_testimonials(request):
    """Admin testimonials management"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    _auto_generate_testimonials()

    testimonials = ClientTestimonial.objects.all().order_by('-created_at')
    published_count = ClientTestimonial.objects.filter(is_published=True).count()
    featured_count = ClientTestimonial.objects.filter(is_featured=True).count()
    avg_rating = 5.0

    if request.method == 'POST':
        action = request.POST.get('action')
        testimonial_id = request.POST.get('testimonial_id')

        try:
            testimonial = ClientTestimonial.objects.get(id=testimonial_id)

            if action == 'publish':
                testimonial.is_published = True
                testimonial.save()
                messages.success(request, 'Testimonial published.')
            elif action == 'unpublish':
                testimonial.is_published = False
                testimonial.save()
                messages.success(request, 'Testimonial unpublished.')
            elif action == 'feature':
                testimonial.is_featured = not testimonial.is_featured
                testimonial.save()
                messages.success(request, f'Testimonial {"featured" if testimonial.is_featured else "unfeatured"}.')
        except ClientTestimonial.DoesNotExist:
            messages.error(request, 'Testimonial not found.')

        return redirect('admin_testimonials')

    context = {
        'testimonials': testimonials,
        'published_count': published_count,
        'featured_count': featured_count,
        'avg_rating': avg_rating,
    }
    return render(request, 'admin/testimonials.html', context)


@login_required
def admin_reports(request):
    """Admin reports and analytics"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    from django.db.models import Count

    # Key metrics
    total_clients = Customer.objects.count()
    total_service_requests = ServiceRequest.objects.count()
    completed_services = ServiceRequest.objects.filter(status='completed').count()
    workshop_attendees = WorkshopRegistration.objects.filter(status='attended').count()

    # Calculate month-over-month changes
    current_month = timezone.now().month
    current_year = timezone.now().year
    last_month = current_month - 1 if current_month > 1 else 12
    last_year = current_year if current_month > 1 else current_year - 1

    current_month_clients = Customer.objects.filter(
        registration_date__month=current_month,
        registration_date__year=current_year
    ).count()
    last_month_clients = Customer.objects.filter(
        registration_date__month=last_month,
        registration_date__year=last_year
    ).count()
    client_change = ((current_month_clients - last_month_clients) / max(last_month_clients, 1)) * 100 if last_month_clients > 0 else 100 if current_month_clients > 0 else 0

    current_month_requests = ServiceRequest.objects.filter(
        created_at__month=current_month,
        created_at__year=current_year
    ).count()
    last_month_requests = ServiceRequest.objects.filter(
        created_at__month=last_month,
        created_at__year=last_year
    ).count()
    request_change = ((current_month_requests - last_month_requests) / max(last_month_requests, 1)) * 100 if last_month_requests > 0 else 100 if current_month_requests > 0 else 0

    current_month_completed = ServiceRequest.objects.filter(
        status='completed',
        completed_at__month=current_month,
        completed_at__year=current_year
    ).count()
    last_month_completed = ServiceRequest.objects.filter(
        status='completed',
        completed_at__month=last_month,
        completed_at__year=last_year
    ).count()
    completed_change = ((current_month_completed - last_month_completed) / max(last_month_completed, 1)) * 100 if last_month_completed > 0 else 100 if current_month_completed > 0 else 0

    current_month_attendees = WorkshopRegistration.objects.filter(
        attended_at__month=current_month,
        attended_at__year=current_year
    ).count()
    last_month_attendees = WorkshopRegistration.objects.filter(
        attended_at__month=last_month,
        attended_at__year=last_year
    ).count()
    attendee_change = ((current_month_attendees - last_month_attendees) / max(last_month_attendees, 1)) * 100 if last_month_attendees > 0 else 100 if current_month_attendees > 0 else 0

    # Top services by request count
    top_services = ResearchService.objects.annotate(
        request_count=Count('service_requests')
    ).order_by('-request_count')[:5]

    # Customer segments
    individual_customers = Customer.objects.filter(customer_type='individual').count()
    organization_customers = Customer.objects.filter(customer_type='organization').count()
    total_customers = individual_customers + organization_customers

    individual_percentage = (individual_customers / total_customers * 100) if total_customers > 0 else 0
    organization_percentage = (organization_customers / total_customers * 100) if total_customers > 0 else 0

    # Request status distribution
    pending_count = ServiceRequest.objects.filter(status='pending').count()
    accepted_count = ServiceRequest.objects.filter(status='accepted').count()
    in_progress_count = ServiceRequest.objects.filter(status='in_progress').count()
    completed_count = ServiceRequest.objects.filter(status='completed').count()
    cancelled_count = ServiceRequest.objects.filter(status='cancelled').count()

    context = {
        'total_clients': total_clients,
        'current_month_clients': current_month_clients,
        'client_change': round(client_change, 1),
        'total_service_requests': total_service_requests,
        'current_month_requests': current_month_requests,
        'request_change': round(request_change, 1),
        'completed_services': completed_services,
        'current_month_completed': current_month_completed,
        'completed_change': round(completed_change, 1),
        'workshop_attendees': workshop_attendees,
        'current_month_attendees': current_month_attendees,
        'attendee_change': round(attendee_change, 1),
        'top_services': top_services,
        'individual_customers': individual_customers,
        'organization_customers': organization_customers,
        'individual_percentage': round(individual_percentage, 1),
        'organization_percentage': round(organization_percentage, 1),
        'pending_count': pending_count,
        'accepted_count': accepted_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
    }
    return render(request, 'admin/reports.html', context)


@login_required
def admin_zoom_appointments(request):
    """Admin Zoom appointments management"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    zoom_appointments = ZoomAppointment.objects.all().order_by('-start_time')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            zoom_link = request.POST.get('zoom_link', '').strip()
            passcode = request.POST.get('passcode', '').strip()
            password = request.POST.get('password', '').strip()
            start_time = request.POST.get('start_time')
            workshop_id = request.POST.get('workshop_id')

            if zoom_link and start_time:
                try:
                    workshop = None
                    if workshop_id:
                        try:
                            workshop = Workshop.objects.get(id=workshop_id)
                        except Workshop.DoesNotExist:
                            pass

                    ZoomAppointment.objects.create(
                        zoom_link=zoom_link,
                        passcode=passcode,
                        password=password,
                        start_time=start_time,
                        workshop=workshop,
                        is_active=True
                    )
                    messages.success(request, 'Zoom appointment created successfully!')
                except Exception as e:
                    messages.error(request, f'Error creating Zoom appointment: {str(e)}')
            else:
                messages.error(request, 'Please fill in all required fields (Zoom Link and Start Time).')

        elif action == 'update':
            try:
                zoom_id = request.POST.get('zoom_id')
                zoom_appointment = ZoomAppointment.objects.get(id=zoom_id)

                zoom_appointment.zoom_link = request.POST.get('zoom_link', zoom_appointment.zoom_link).strip()
                zoom_appointment.passcode = request.POST.get('passcode', '').strip()
                zoom_appointment.password = request.POST.get('password', '').strip()
                zoom_appointment.start_time = request.POST.get('start_time', zoom_appointment.start_time)
                zoom_appointment.save()

                messages.success(request, 'Zoom appointment updated successfully!')
            except ZoomAppointment.DoesNotExist:
                messages.error(request, 'Zoom appointment not found.')
            except Exception as e:
                messages.error(request, f'Error updating Zoom appointment: {str(e)}')

        elif action == 'delete':
            try:
                zoom_id = request.POST.get('zoom_id')
                zoom_appointment = ZoomAppointment.objects.get(id=zoom_id)
                zoom_appointment.delete()
                messages.success(request, 'Zoom appointment deleted successfully.')
            except ZoomAppointment.DoesNotExist:
                messages.error(request, 'Zoom appointment not found.')

        elif action == 'toggle_status':
            try:
                zoom_id = request.POST.get('zoom_id')
                zoom_appointment = ZoomAppointment.objects.get(id=zoom_id)
                zoom_appointment.is_active = not zoom_appointment.is_active
                zoom_appointment.save()
                status = 'activated' if zoom_appointment.is_active else 'deactivated'
                messages.success(request, f'Zoom appointment {status}.')
            except ZoomAppointment.DoesNotExist:
                messages.error(request, 'Zoom appointment not found.')

        return redirect('admin_zoom_appointments')

    # Get workshops for the dropdown
    workshops = Workshop.objects.filter(is_active=True).order_by('-date')

    context = {
        'zoom_appointments': zoom_appointments,
        'workshops': workshops,
    }
    return render(request, 'admin/zoom_appointments.html', context)


@login_required
def admin_leadership(request):
    """Admin leadership management"""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')

    from .models import Leadership

    leadership_members = Leadership.objects.all().order_by('display_order')
    active_count = Leadership.objects.filter(is_active=True).count()

    if request.method == 'POST':
        action = request.POST.get('action')
        member_id = request.POST.get('member_id')

        try:
            member = Leadership.objects.get(id=member_id)

            if action == 'toggle_active':
                member.is_active = not member.is_active
                member.save()
                messages.success(request, f'Member {"activated" if member.is_active else "deactivated"}.')
            elif action == 'delete':
                member.delete()
                messages.success(request, 'Leadership member deleted.')
        except Leadership.DoesNotExist:
            messages.error(request, 'Leadership member not found.')

        return redirect('admin_leadership')

    context = {
        'leadership_members': leadership_members,
        'active_count': active_count,
    }
    return render(request, 'admin/leadership.html', context)


def privacy(request):
    """Privacy policy page"""
    return render(request, 'privacy.html')


def terms(request):
    """Terms of service page"""
    return render(request, 'terms.html')
