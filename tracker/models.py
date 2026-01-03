from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import URLValidator, EmailValidator
from django.db.models import Q


class Customer(models.Model):
    """Customer/Client model"""
    CUSTOMER_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('organization', 'Organization'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='customer_profile')
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPE_CHOICES, default='individual')
    registration_date = models.DateTimeField(auto_now_add=True)
    last_contact = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def get_total_requests(self):
        return self.service_requests.count()
    
    def get_completed_requests(self):
        return self.service_requests.filter(status='completed').count()


class ResearchService(models.Model):
    """Research services offered"""
    CATEGORY_CHOICES = (
        ('concept_proposal', 'Concept Proposal'),
        ('thesis', 'Thesis Writing'),
        ('articles', 'Article Writing'),
        ('data_analysis', 'Data Analysis'),
        ('research_design', 'Research Design'),
        ('consultancy', 'Consultancy'),
        ('training_capacity', 'Training & Capacity Building'),
    )
    
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, default='ri-file-text-line')
    price_from = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_to = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    turnaround_time = models.CharField(max_length=100, blank=True, help_text="e.g., '5-7 business days'")
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_pending_requests(self):
        return self.service_requests.filter(status='pending').count()
    
    def get_completed_requests(self):
        return self.service_requests.filter(status='completed').count()


class ConsultancySubService(models.Model):
    """Consultancy sub-services"""
    CONSULTANCY_TYPES = (
        ('business_tax', 'Business & Tax Consulting'),
        ('business_strategy', 'Business Strategy & Planning'),
        ('investment', 'Investment Facilitation'),
        ('proposal_support', 'Proposal & Academic Wig Support'),
        ('training_capacity', 'Training & Capacity Building'),
        ('academic', 'Academic Consultancy'),
        ('research', 'Research Consultancy'),
        ('career', 'Career Consultancy'),
        ('writing', 'Writing Consultancy'),
    )

    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    consultancy_type = models.CharField(max_length=50, choices=CONSULTANCY_TYPES)
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    features = models.TextField(blank=True, help_text="List of features/items, one per line")
    icon = models.CharField(max_length=100, default='ri-discuss-line', help_text="e.g., ri-briefcase-line, ri-team-line")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def get_features_list(self):
        """Return features as a list"""
        if self.features:
            return [f.strip() for f in self.features.split('\n') if f.strip()]
        return []


class ServiceRequest(models.Model):
    """Customer service requests"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='service_requests')
    service = models.ForeignKey(ResearchService, on_delete=models.SET_NULL, null=True, blank=True, related_name='service_requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField(null=True, blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, help_text="Internal notes from admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.customer.full_name}"
    
    def days_until_deadline(self):
        if self.deadline:
            delta = self.deadline - timezone.now()
            return delta.days
        return None
    
    def is_overdue(self):
        if self.deadline and self.status != 'completed':
            return timezone.now() > self.deadline
        return False


class Workshop(models.Model):
    """Workshops and training sessions"""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField()
    detailed_description = models.TextField(blank=True)
    date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    is_online = models.BooleanField(default=False)
    meeting_url = models.URLField(blank=True, help_text="Zoom/Teams link for online workshops")
    max_participants = models.IntegerField(null=True, blank=True)
    facilitator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='workshops')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_registration_count(self):
        return self.registrations.filter(status='registered').count()
    
    def is_full(self):
        if self.max_participants:
            return self.get_registration_count() >= self.max_participants
        return False
    
    def is_upcoming(self):
        return self.date > timezone.now()
    
    def is_past(self):
        return self.date < timezone.now()


class WorkshopRegistration(models.Model):
    """Workshop registration"""
    STATUS_CHOICES = (
        ('registered', 'Registered'),
        ('attended', 'Attended'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No-show'),
    )
    
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE, related_name='registrations')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='workshop_registrations')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended_at = models.DateTimeField(null=True, blank=True)
    special_requirements = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('workshop', 'customer')
        ordering = ['-registered_at']
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.workshop.title}"


class ZoomAppointment(models.Model):
    """Zoom appointment for workshops/trainings"""
    workshop = models.OneToOneField(Workshop, on_delete=models.CASCADE, related_name='zoom_appointment', null=True, blank=True)
    service = models.ForeignKey(ConsultancySubService, on_delete=models.SET_NULL, null=True, blank=True, related_name='zoom_appointments')
    zoom_link = models.URLField(help_text="Zoom meeting link")
    zoom_meeting_id = models.CharField(max_length=100, blank=True, help_text="Zoom meeting ID")
    passcode = models.CharField(max_length=100, blank=True, help_text="Zoom meeting passcode")
    password = models.CharField(max_length=100, blank=True, help_text="Additional password if needed")
    start_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        if self.workshop:
            return f"Zoom: {self.workshop.title}"
        return f"Zoom Appointment - {self.start_time}"


class ClientTestimonial(models.Model):
    """Client testimonials and reviews"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='testimonials')
    service = models.ForeignKey(ResearchService, on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    quote = models.TextField()
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return f"Testimonial from {self.customer.full_name}"


class UserProfile(models.Model):
    """Extended user profile with additional fields"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    newsletter_subscribed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"


class Notification(models.Model):
    """User notifications"""
    NOTIFICATION_TYPES = (
        ('service_update', 'Service Update'),
        ('workshop_reminder', 'Workshop Reminder'),
        ('message', 'Message'),
        ('system', 'System'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.URLField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return self.title


class CompanyProfile(models.Model):
    """Company profile and settings"""
    # Basic Information
    company_name = models.CharField(max_length=255, default="The Writing Hub Tz")
    tagline = models.CharField(max_length=500, blank=True, default="Empowering Excellence through Words")

    # Contact Information
    phone = models.CharField(max_length=20, blank=True, default="+255 (0) 717 313797")
    email = models.EmailField(blank=True, default="thewritinghubtz@gmail.com")
    website = models.URLField(blank=True, default="www.thewritinghutz.net")
    address = models.TextField(blank=True, default="9 Floor, Elite Towers, Azikiwe St, Dar es Salaam, Tanzania")

    # Social Media
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    instagram = models.URLField(blank=True, default="the_writing_hub_tz")

    # Company Story
    founder_name = models.CharField(max_length=255, blank=True, default="Frank Mhando (MA., PhD. DT)")
    founder_title = models.CharField(max_length=255, blank=True, default="Founder")
    founder_affiliation = models.CharField(max_length=255, blank=True, default="University of Johannesburg, SA")

    advisor_name = models.CharField(max_length=255, blank=True, default="Prof. Donaldson F. Conserve")
    advisor_title = models.CharField(max_length=255, blank=True, default="Advisor")
    advisor_affiliation = models.CharField(max_length=255, blank=True, default="The George Washington University, USA")

    company_story = models.TextField(blank=True)

    # Vision & Mission
    vision = models.TextField(blank=True, default="To be the leading catalyst for academic, research and professional success by fostering exceptional writing skills and promoting impactful communication.")
    mission = models.TextField(blank=True, default="At The Writing Hub Tz, our mission is to provide comprehensive writing solutions, research and development support, educational support and to empowering individuals and organisations in achieving their goals. We strive to offer unparalleled guidance, coaching, and workshops that cultivate strong writing abilities and research acumen. With a commitment to excellence, we aim to bridge the gap between ideas and expression, enabling our clients to make a lasting impact in academia and beyond.")

    # Why Choose Us
    why_choose_us = models.TextField(blank=True, default="Choose 'The Writing Hub Tz' for expert guidance and personalized support in academic writing, research and development services, workshops, business write-ups, and streamlined government application facilitation. With a proven track record, our experienced team is committed to empowering you to excel in your academic, research, professional, and entrepreneurial pursuits.")

    # Business Information
    registration_year = models.IntegerField(blank=True, default=2023)
    established_year = models.IntegerField(blank=True, default=2018)

    # Display Settings
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Profile"
        verbose_name_plural = "Company Profile"

    def __str__(self):
        return self.company_name

    @classmethod
    def get_profile(cls):
        """Get the company profile (singleton pattern)"""
        profile, _ = cls.objects.get_or_create(pk=1)
        return profile
