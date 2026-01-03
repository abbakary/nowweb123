# ResearchHub Setup Instructions

## Project Overview
ResearchHub is a comprehensive Django application for managing research services, client requests, workshops, and consultancy services. It includes a complete authentication system with beautiful login/register pages, user profiles, and admin dashboard.

## Features Implemented

### Authentication System
- **User Registration** - Beautiful signup page with password strength checker
- **User Login** - Login with email or username, remember me functionality
- **Password Management** - Change password with strength validation
- **Password Reset** - Email-based password reset functionality
- **User Profiles** - Complete profile management with avatar upload

### User Management
- **User Dashboard** - View service requests, workshops, and statistics
- **Profile Settings** - Edit personal information, preferences, and notifications
- **Account Settings** - Manage notifications, privacy, security settings

### Service Management
- **Research Services** - Create and manage research services
- **Consultancy Services** - Manage consultancy sub-services
- **Service Requests** - Clients can request services with deadlines and budgets
- **Pricing Management** - Set service pricing and turnaround times

### Workshop Management
- **Workshop Creation** - Create online and in-person workshops
- **Workshop Registration** - Users can register for workshops
- **Participant Management** - Track participants and attendance

### Client Management
- **Customer Profiles** - Detailed customer information
- **Testimonials** - Manage client testimonials and reviews
- **Service History** - Track all client service requests and interactions

### Admin Dashboard
- **Overview Analytics** - View key statistics and metrics
- **Service Management** - CRUD operations for all services
- **Client Management** - View and manage all clients
- **Request Management** - Update service request status
- **Workshop Management** - Create and manage workshops
- **Testimonial Moderation** - Publish/feature testimonials

### API Endpoints
- Check username/email availability
- Get services list (JSON)
- Get testimonials (JSON)
- Get workshops (JSON)
- Submit contact forms via AJAX

## Database Models

### Core Models
- **Customer** - Client information and contact details
- **ResearchService** - Available research services
- **ConsultancySubService** - Consultancy service options
- **ServiceRequest** - Client service requests with status tracking
- **Workshop** - Training sessions and events
- **WorkshopRegistration** - Workshop participant tracking
- **ClientTestimonial** - Client reviews and testimonials
- **UserProfile** - Extended user profile information
- **Notification** - User notifications system

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser (Admin Account)
```bash
python manage.py createsuperuser
```

### 4. Load Sample Data (Optional)
You can add sample services and workshops through the admin panel or create a data fixture.

### 5. Run Development Server
```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000`

## URL Routes

### Frontend Routes
- `/` - Home page
- `/services/` - Services listing
- `/service/<id>/` - Service detail page
- `/service/<id>/request/` - Service request form
- `/contact/` - Contact page
- `/about/` - About page
- `/workshop/<id>/` - Workshop detail page
- `/workshop/<id>/register/` - Workshop registration
- `/dashboard/` - Client dashboard (requires login)

### Authentication Routes
- `/login/` - Login page
- `/register/` - Registration page
- `/logout/` - Logout
- `/password-reset/` - Password reset request
- `/password-reset/<uidb64>/<token>/` - Password reset confirmation

### User Profile Routes
- `/profile/` - View user profile
- `/profile/edit/` - Edit profile
- `/profile/password-change/` - Change password
- `/profile/settings/` - Account settings

### Admin Routes
- `/admin/` - Django admin panel
- `/admin/dashboard/` - Admin dashboard
- `/admin/services/` - Manage services
- `/admin/clients/` - Manage clients
- `/admin/requests/` - Manage service requests
- `/admin/workshops/` - Manage workshops
- `/admin/testimonials/` - Manage testimonials

### API Routes
- `/api/check-username/` - Check username availability (POST)
- `/api/check-email/` - Check email availability (POST)
- `/api/get-services/` - Get services list (GET)
- `/api/get-testimonials/` - Get testimonials (GET)
- `/api/get-workshops/` - Get upcoming workshops (GET)
- `/api/submit-contact/` - Submit contact form (POST)

## Admin Panel Features

The Django admin panel includes:
- **Customer Management** - View, search, and filter customers
- **Service Management** - Create, edit, delete services
- **Request Management** - Track and update service requests with status badges
- **Workshop Management** - Create and manage workshops with participant tracking
- **Testimonial Moderation** - Approve and feature testimonials
- **User Profile Management** - Manage extended user profiles

## Authentication

### Login
- Users can login with username or email
- Password must be at least 8 characters
- "Remember me" option for extended session (2 weeks)

### Registration
- Email validation (must be unique)
- Username validation (must be unique)
- Password strength indicator
- Automatic customer profile creation
- Email verification (can be implemented)

### Password Reset
- Email-based password reset
- Secure token-based reset links
- New password strength validation

## Security Features

- CSRF protection on all forms
- Password hashing using Django's default algorithm
- Session timeout (2 weeks for "Remember me")
- SQL injection protection (using Django ORM)
- XSS protection
- Secure password reset tokens

## Template Structure

All templates extend from `base.html` which includes:
- Navigation bar with user menu
- CSS variables for consistent branding
- Bootstrap 5 integration
- RemixIcon library for icons
- Message handling for user feedback
- Responsive design

## Static Files

Static files are organized in:
- `static/js/` - JavaScript files
- `static/css/` - CSS stylesheets
- `static/images/` - Image assets

## Media Files

User uploads (avatars, documents) are stored in:
- `media/avatars/` - User profile avatars
- `media/uploads/` - Other uploaded files

## Configuration

Key settings in `settings.py`:
- Database: MySQL (default localhost:3306)
- Time Zone: Asia/Riyadh
- Static Files: In `tracker/static/`
- Media Files: In `media/`
- Session Timeout: 2 weeks

## Customization

### Colors and Styling
Edit CSS variables in `base.html`:
```css
--primary: #1e3c72;
--accent: #f39c12;
--dark: #1a1a1a;
--light: #f8f9fa;
```

### Add New Services
1. Go to Admin Panel
2. Click "Services" under Tracker
3. Click "Add Service"
4. Fill in details and save

### Create Workshops
1. Go to Admin Dashboard
2. Click "Create Workshop"
3. Fill in details (date, location, capacity)
4. Save and publish

## Troubleshooting

### Database Errors
- Check MySQL is running: `mysql -u root -p`
- Verify credentials in settings.py
- Run migrations: `python manage.py migrate`

### Static Files Not Loading
- Collect static files: `python manage.py collectstatic`
- Check `STATIC_ROOT` and `STATIC_URL` in settings.py

### Import Errors
- Install missing packages: `pip install -r requirements.txt`
- Check Python version (3.9+)

## Next Steps

1. Create sample data through admin panel
2. Customize email templates for password reset
3. Set up email backend (SMTP) for notifications
4. Implement payment processing if needed
5. Add more analytics features
6. Set up automated backups
7. Configure CDN for static files

## Support

For questions or issues:
1. Check logs in `debug.log`
2. Review Django error pages in development
3. Check email template configuration
4. Verify database connection

## License & Credits

This is a professional research services management system built with Django.
