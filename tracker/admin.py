from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Customer, ResearchService, ConsultancySubService, ServiceRequest,
    Workshop, WorkshopRegistration, ClientTestimonial, UserProfile,
    Notification, CompanyProfile, Leadership, ServiceImage, TutorialVideo, ServiceFAQ
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'customer_type', 'registration_date', 'is_active')
    list_filter = ('customer_type', 'is_active', 'registration_date')
    search_fields = ('full_name', 'email', 'phone', 'organization')
    readonly_fields = ('registration_date', 'last_contact')
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'email', 'full_name', 'phone', 'organization')
        }),
        ('Account Details', {
            'fields': ('customer_type', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('registration_date', 'last_contact'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResearchService)
class ResearchServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_range', 'is_active', 'display_order')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'slug', 'category', 'description', 'detailed_description', 'icon')
        }),
        ('Pricing', {
            'fields': ('price_from', 'price_to', 'turnaround_time')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
    )
    
    def price_range(self, obj):
        if obj.price_from and obj.price_to:
            return f"${obj.price_from} - ${obj.price_to}"
        elif obj.price_from:
            return f"From ${obj.price_from}"
        return "Price upon request"
    price_range.short_description = "Price Range"


@admin.register(ConsultancySubService)
class ConsultancySubServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'consultancy_type', 'hourly_rate', 'is_active')
    list_filter = ('consultancy_type', 'is_active')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'consultancy_type', 'description', 'detailed_description', 'icon')
        }),
        ('Pricing', {
            'fields': ('hourly_rate',)
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
    )


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer_link', 'service', 'status_badge', 'deadline', 'created_at')
    list_filter = ('status', 'created_at', 'service')
    search_fields = ('title', 'description', 'customer__full_name', 'customer__email')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    fieldsets = (
        ('Request Information', {
            'fields': ('customer', 'service', 'title', 'description')
        }),
        ('Details', {
            'fields': ('deadline', 'budget', 'assigned_to')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def customer_link(self, obj):
        return obj.customer.full_name
    customer_link.short_description = "Customer"
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FF9800',
            'accepted': '#2196F3',
            'in_progress': '#03A9F4',
            'completed': '#4CAF50',
            'cancelled': '#F44336'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#999'),
            obj.get_status_display()
        )
    status_badge.short_description = "Status"


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'location_display', 'participant_count', 'is_active')
    list_filter = ('is_active', 'is_online', 'date')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Workshop Information', {
            'fields': ('title', 'slug', 'description', 'detailed_description')
        }),
        ('Schedule & Location', {
            'fields': ('date', 'location', 'is_online', 'meeting_url')
        }),
        ('Details', {
            'fields': ('facilitator', 'price', 'max_participants')
        }),
        ('Settings', {
            'fields': ('is_active',)
        }),
    )
    
    def location_display(self, obj):
        if obj.is_online:
            return format_html('<span style="color: blue;">🌐 Online</span>')
        return obj.location
    location_display.short_description = "Location"
    
    def participant_count(self, obj):
        count = obj.get_registration_count()
        max_p = obj.max_participants
        if max_p:
            return f"{count}/{max_p}"
        return str(count)
    participant_count.short_description = "Participants"


@admin.register(WorkshopRegistration)
class WorkshopRegistrationAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'workshop', 'status', 'registered_at')
    list_filter = ('status', 'registered_at', 'workshop')
    search_fields = ('customer__full_name', 'workshop__title')
    readonly_fields = ('registered_at', 'attended_at')
    
    def customer_name(self, obj):
        return obj.customer.full_name
    customer_name.short_description = "Customer"


@admin.register(ClientTestimonial)
class ClientTestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'rating_stars', 'service', 'published_status', 'created_at')
    list_filter = ('is_published', 'is_featured', 'rating', 'created_at')
    search_fields = ('customer__full_name', 'quote', 'service__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Testimonial', {
            'fields': ('customer', 'service', 'rating', 'quote')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured')
        }),
    )
    
    def customer_name(self, obj):
        return obj.customer.full_name
    customer_name.short_description = "Customer"
    
    def rating_stars(self, obj):
        stars = '⭐' * obj.rating
        return format_html(f'<span>{stars}</span>')
    rating_stars.short_description = "Rating"
    
    def published_status(self, obj):
        if obj.is_published:
            return format_html('<span style="color: green;">✓ Published</span>')
        return format_html('<span style="color: orange;">⊘ Draft</span>')
    published_status.short_description = "Status"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'email_verified', 'phone_verified', 'newsletter_subscribed', 'created_at')
    list_filter = ('email_verified', 'phone_verified', 'newsletter_subscribed', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def username(self, obj):
        return obj.user.username
    username.short_description = "User"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_link', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at',)

    def user_link(self, obj):
        return obj.user.username
    user_link.short_description = "User"


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'email', 'phone', 'is_active')
    fieldsets = (
        ('Basic Information', {
            'fields': ('company_name', 'tagline')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'linkedin', 'instagram')
        }),
        ('Leadership', {
            'fields': ('founder_name', 'founder_title', 'founder_affiliation',
                      'advisor_name', 'advisor_title', 'advisor_affiliation')
        }),
        ('Company Content', {
            'fields': ('company_story', 'vision', 'mission', 'why_choose_us')
        }),
        ('Business Information', {
            'fields': ('registration_year', 'established_year')
        }),
        ('Display Settings', {
            'fields': ('is_active',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def has_add_permission(self, request):
        return not CompanyProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Leadership)
class LeadershipAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'photo_preview', 'display_order', 'is_active')
    list_filter = ('is_active', 'display_order')
    search_fields = ('name', 'title', 'affiliation', 'bio')
    readonly_fields = ('created_at', 'updated_at', 'photo_preview')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'title', 'affiliation', 'bio')
        }),
        ('Photo', {
            'fields': ('photo', 'photo_preview'),
            'description': 'Upload a professional photo (recommended size: 400x500px)'
        }),
        ('Contact Information', {
            'fields': ('email', 'phone'),
            'classes': ('collapse',)
        }),
        ('Social Media', {
            'fields': ('facebook', 'twitter', 'linkedin', 'instagram'),
            'classes': ('collapse',)
        }),
        ('Display Settings', {
            'fields': ('display_order', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" width="100" height="125" style="object-fit: cover; border-radius: 4px;" />',
                obj.photo.url
            )
        return "No photo"
    photo_preview.short_description = "Photo Preview"


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ('service', 'title', 'image_preview', 'is_featured', 'display_order')
    list_filter = ('is_featured', 'service', 'created_at')
    search_fields = ('service__name', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    fieldsets = (
        ('Image Information', {
            'fields': ('service', 'title', 'image', 'image_preview')
        }),
        ('Details', {
            'fields': ('description', 'is_featured')
        }),
        ('Display', {
            'fields': ('display_order',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="150" height="100" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(TutorialVideo)
class TutorialVideoAdmin(admin.ModelAdmin):
    list_display = ('service', 'title', 'duration', 'published_status', 'display_order', 'created_at')
    list_filter = ('is_published', 'service', 'created_at')
    search_fields = ('service__name', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Video Information', {
            'fields': ('service', 'title', 'description')
        }),
        ('Video Details', {
            'fields': ('video_url', 'duration', 'thumbnail')
        }),
        ('Publishing', {
            'fields': ('is_published', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def published_status(self, obj):
        if obj.is_published:
            return format_html('<span style="color: green;">✓ Published</span>')
        return format_html('<span style="color: orange;">⊘ Draft</span>')
    published_status.short_description = "Status"


@admin.register(ServiceFAQ)
class ServiceFAQAdmin(admin.ModelAdmin):
    list_display = ('service', 'question_preview', 'published_status', 'display_order')
    list_filter = ('is_published', 'service', 'created_at')
    search_fields = ('service__name', 'question', 'answer')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('FAQ Information', {
            'fields': ('service', 'question', 'answer')
        }),
        ('Publishing', {
            'fields': ('is_published', 'display_order')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def question_preview(self, obj):
        return obj.question[:75] + '...' if len(obj.question) > 75 else obj.question
    question_preview.short_description = "Question"

    def published_status(self, obj):
        if obj.is_published:
            return format_html('<span style="color: green;">✓ Published</span>')
        return format_html('<span style="color: orange;">⊘ Draft</span>')
    published_status.short_description = "Status"
