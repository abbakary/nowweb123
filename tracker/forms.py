from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, PasswordResetForm
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from .models import Customer, UserProfile, ServiceRequest, ClientTestimonial, Workshop, WorkshopRegistration, ResearchService


class CustomUserCreationForm(UserCreationForm):
    """Custom user registration form - email based"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'autocomplete': 'email',
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567',
            'autocomplete': 'tel',
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter a strong password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = User
        fields = ('email', 'phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.email = email
        user.username = email
        if commit:
            user.save()
        return user


class CustomUserLoginForm(forms.Form):
    """Custom user login form - username or email"""
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or email',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )


class CustomerProfileForm(forms.ModelForm):
    """Customer profile update form"""
    class Meta:
        model = Customer
        fields = ('full_name', 'email', 'phone', 'organization', 'customer_type')
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email address',
                'readonly': 'readonly',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number',
            }),
            'organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Organization (optional)',
            }),
            'customer_type': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


class UserProfileForm(forms.ModelForm):
    """User profile extended fields form"""
    class Meta:
        model = UserProfile
        fields = ('bio', 'avatar', 'newsletter_subscribed')
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us about yourself',
                'rows': 4,
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'newsletter_subscribed': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class CustomPasswordChangeForm(PasswordChangeForm):
    """Custom password change form"""
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your current password',
            'autocomplete': 'current-password',
        })
    )
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password',
        })
    )
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password',
        })
    )


class ServiceRequestForm(forms.ModelForm):
    """Service request form"""
    class Meta:
        model = ServiceRequest
        fields = ('title', 'description', 'deadline', 'budget')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Request title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your requirements in detail',
                'rows': 5,
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Budget (optional)',
                'min': '0',
                'step': '0.01',
            }),
        }


class ClientTestimonialForm(forms.ModelForm):
    """Testimonial submission form"""
    class Meta:
        model = ClientTestimonial
        fields = ('service', 'rating', 'quote')
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-control',
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control',
            }),
            'quote': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with us',
                'rows': 4,
            }),
        }


class WorkshopRegistrationForm(forms.ModelForm):
    """Workshop registration form"""
    class Meta:
        model = WorkshopRegistration
        fields = ('special_requirements',)
        widgets = {
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any special requirements or accessibility needs?',
                'rows': 3,
            }),
        }


class ContactForm(forms.Form):
    """Contact form for general inquiries"""
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name',
            'required': 'required',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address',
            'required': 'required',
        })
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your phone number (optional)',
        })
    )
    service = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    subject = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject',
            'required': 'required',
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your message',
            'rows': 5,
            'required': 'required',
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ResearchService
        self.fields['service'].queryset = ResearchService.objects.filter(is_active=True)
        self.fields['service'].label = 'Service of Interest (optional)'


class AdminServiceForm(forms.ModelForm):
    """Admin form for managing services"""
    class Meta:
        model = ResearchService
        fields = (
            'name', 'slug', 'category', 'description', 'detailed_description',
            'icon', 'price_from', 'price_to', 'turnaround_time', 'display_order', 'is_active'
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'detailed_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ri-file-text-line'}),
            'price_from': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_to': forms.NumberInput(attrs={'class': 'form-control'}),
            'turnaround_time': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 5-7 business days'}),
            'display_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PasswordResetRequestForm(forms.Form):
    """Password reset request form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'autocomplete': 'email',
        })
    )


class PasswordResetConfirmForm(forms.Form):
    """Password reset confirmation form"""
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'autocomplete': 'new-password',
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'autocomplete': 'new-password',
        })
    )
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        return password2
