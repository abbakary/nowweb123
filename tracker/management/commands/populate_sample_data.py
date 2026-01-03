from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from tracker.models import (
    Customer, ResearchService, ConsultancySubService, ServiceRequest,
    Workshop, WorkshopRegistration, ClientTestimonial, UserProfile
)


class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate sample data...')
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # self._clear_data()
        
        # Create sample users and customers
        admin_user = self._create_admin_user()
        sample_users = self._create_sample_users()
        
        # Create research services
        services = self._create_research_services()
        
        # Create consultancy services
        consultancy_services = self._create_consultancy_services()
        
        # Create workshops
        workshops = self._create_workshops()
        
        # Create service requests
        service_requests = self._create_service_requests(sample_users, services)
        
        # Create testimonials (will auto-generate from completed requests)
        self._create_testimonials(sample_users, services)
        
        self.stdout.write(self.style.SUCCESS('✓ Sample data populated successfully!'))
        self.stdout.write(self.style.SUCCESS(f'  - Admin user: admin@thewritinghutz.net / password'))
        self.stdout.write(self.style.SUCCESS(f'  - Sample users: {len(sample_users)} created'))
        self.stdout.write(self.style.SUCCESS(f'  - Research services: {services.count()} created'))
        self.stdout.write(self.style.SUCCESS(f'  - Consultancy services: {consultancy_services.count()} created'))
        self.stdout.write(self.style.SUCCESS(f'  - Workshops: {len(workshops)} created'))
        self.stdout.write(self.style.SUCCESS(f'  - Service requests: {service_requests.count()} created'))

    def _clear_data(self):
        """Clear existing data"""
        self.stdout.write('Clearing existing data...')
        User.objects.filter(is_staff=False).delete()
        ResearchService.objects.all().delete()
        ConsultancySubService.objects.all().delete()
        Workshop.objects.all().delete()

    def _create_admin_user(self):
        """Create or get admin user"""
        admin, created = User.objects.get_or_create(
            username='admin@thewritinghutz.net',
            defaults={
                'email': 'admin@thewritinghutz.net',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('password')
            admin.save()
            self.stdout.write(f'✓ Created admin user: {admin.email}')
        return admin

    def _create_sample_users(self):
        """Create sample users"""
        users = []
        sample_users_data = [
            {
                'email': 'john.smith@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '+1-555-0101',
                'customer_type': 'individual',
            },
            {
                'email': 'sarah.johnson@example.com',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'phone': '+1-555-0102',
                'customer_type': 'individual',
            },
            {
                'email': 'michael.chen@example.com',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'phone': '+1-555-0103',
                'customer_type': 'individual',
            },
            {
                'email': 'emma.wilson@example.com',
                'first_name': 'Emma',
                'last_name': 'Wilson',
                'phone': '+1-555-0104',
                'customer_type': 'organization',
                'organization': 'University of Cambridge',
            },
            {
                'email': 'david.brown@example.com',
                'first_name': 'David',
                'last_name': 'Brown',
                'phone': '+1-555-0105',
                'customer_type': 'individual',
            },
            {
                'email': 'lisa.garcia@example.com',
                'first_name': 'Lisa',
                'last_name': 'Garcia',
                'phone': '+1-555-0106',
                'customer_type': 'organization',
                'organization': 'Stanford Research Institute',
            },
        ]
        
        for user_data in sample_users_data:
            email = user_data.pop('email')
            phone = user_data.pop('phone')
            customer_type = user_data.pop('customer_type', 'individual')
            organization = user_data.pop('organization', '')
            
            user, created = User.objects.get_or_create(
                username=email,
                defaults={
                    'email': email,
                    **user_data,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            # Create customer profile
            customer, _ = Customer.objects.get_or_create(
                email=email,
                defaults={
                    'full_name': f"{user.first_name} {user.last_name}",
                    'phone': phone,
                    'customer_type': customer_type,
                    'organization': organization,
                    'user': user,
                }
            )
            
            # Create user profile
            UserProfile.objects.get_or_create(user=user)
            
            users.append(user)
        
        self.stdout.write(f'✓ Created {len(users)} sample users')
        return users

    def _create_research_services(self):
        """Create research services"""
        services_data = [
            {
                'name': 'Thesis Writing & Editing',
                'category': 'thesis',
                'description': 'Professional thesis writing, editing, and formatting for all academic levels',
                'detailed_description': 'Our experienced thesis writers provide comprehensive support from topic selection to final submission. We ensure academic integrity, proper citation, and high-quality content tailored to your institution requirements.',
                'icon': 'ri-file-text-line',
                'price_from': 1500,
                'price_to': 5000,
                'turnaround_time': '7-14 days',
                'display_order': 1,
                'is_active': True,
            },
            {
                'name': 'Research Paper Writing',
                'category': 'articles',
                'description': 'High-quality research papers written by subject matter experts',
                'detailed_description': 'We write original research papers across all disciplines. Our team ensures thorough literature review, proper methodology, and compelling results presentation.',
                'icon': 'ri-article-line',
                'price_from': 800,
                'price_to': 3000,
                'turnaround_time': '5-10 days',
                'display_order': 2,
                'is_active': True,
            },
            {
                'name': 'Data Analysis & Statistics',
                'category': 'data_analysis',
                'description': 'Expert statistical analysis using SPSS, R, Python, and more',
                'detailed_description': 'Our data scientists provide comprehensive data analysis services including descriptive statistics, hypothesis testing, regression analysis, and advanced quantitative methods.',
                'icon': 'ri-bar-chart-line',
                'price_from': 600,
                'price_to': 2500,
                'turnaround_time': '3-7 days',
                'display_order': 3,
                'is_active': True,
            },
            {
                'name': 'Research Design & Methodology',
                'category': 'research_design',
                'description': 'Help with research design, sampling, and methodological frameworks',
                'detailed_description': 'Expert guidance on designing robust research methodologies. We help with sampling strategy, research questions, hypothesis development, and appropriate research design selection.',
                'icon': 'ri-lightbulb-line',
                'price_from': 500,
                'price_to': 2000,
                'turnaround_time': '2-5 days',
                'display_order': 4,
                'is_active': True,
            },
            {
                'name': 'Literature Review Writing',
                'category': 'articles',
                'description': 'Comprehensive literature reviews synthesizing current research',
                'detailed_description': 'We conduct thorough literature searches and synthesize findings into well-organized, critical literature reviews that support your research framework.',
                'icon': 'ri-book-line',
                'price_from': 400,
                'price_to': 1500,
                'turnaround_time': '4-8 days',
                'display_order': 5,
                'is_active': True,
            },
            {
                'name': 'Concept Proposal Development',
                'category': 'concept_proposal',
                'description': 'Develop compelling research proposals and project concepts',
                'detailed_description': 'We help develop strong research proposals that clearly articulate your research problem, objectives, methodology, and significance.',
                'icon': 'ri-bulb-flash-line',
                'price_from': 300,
                'price_to': 1000,
                'turnaround_time': '2-4 days',
                'display_order': 6,
                'is_active': True,
            },
        ]
        
        services = []
        for service_data in services_data:
            service, created = ResearchService.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data,
            )
            services.append(service)
        
        self.stdout.write(f'✓ Created {len(services)} research services')
        return ResearchService.objects.filter(is_active=True)

    def _create_consultancy_services(self):
        """Create consultancy services"""
        consultancy_data = [
            {
                'name': 'Business & Tax Consulting',
                'consultancy_type': 'business_tax',
                'description': 'Tax registration, filing & compliance - Tax advisory /planning - Revenue authority liaison (TRA support)',
                'detailed_description': 'Professional business and tax consulting services including company registration, tax compliance, filing assistance, and revenue authority liaison support.',
                'icon': 'ri-briefcase-4-line',
                'hourly_rate': 150,
                'display_order': 1,
                'is_active': True,
                'features': 'Tax registration\nCompliance filing\nTax advisory\nRevenue authority liaison (TRA support)',
            },
            {
                'name': 'Business Strategy & Planning',
                'consultancy_type': 'business_strategy',
                'description': 'Strategic plans, action plans & business plans - Feasibility studies & market research - Strategy execution support',
                'detailed_description': 'Comprehensive business strategy consultation including business plan development, market research, feasibility studies, and strategic implementation support.',
                'icon': 'ri-map-pin-2-line',
                'hourly_rate': 140,
                'display_order': 2,
                'is_active': True,
                'features': 'Strategic planning\nAction plan development\nFeasibility studies\nMarket research\nStrategy execution support',
            },
            {
                'name': 'Investment Facilitation',
                'consultancy_type': 'investment',
                'description': 'Company registration & compliance (BRELA, TI, ZITPA etc.) - Residence & work permit applications - Business licenses & regulatory approvals',
                'detailed_description': 'Expert guidance on investment facilitation including company registration, compliance with regulatory bodies, permit applications, and business licensing.',
                'icon': 'ri-bank-card-line',
                'hourly_rate': 130,
                'display_order': 3,
                'is_active': True,
                'features': 'Company registration (BRELA)\nCompliance filing\nWork permit applications\nBusiness licenses\nRegulatory approvals',
            },
            {
                'name': 'Proposal & Academic Support',
                'consultancy_type': 'proposal_support',
                'description': 'Research proposals, dissertations, professional reports',
                'detailed_description': 'Professional support for developing research proposals, dissertations, and high-quality academic reports tailored to your specific requirements.',
                'icon': 'ri-file-list-line',
                'hourly_rate': 120,
                'display_order': 4,
                'is_active': True,
                'features': 'Research proposal writing\nDissertation support\nAcademic report writing\nProposal review and feedback',
            },
            {
                'name': 'Training & Capacity Building',
                'consultancy_type': 'training_capacity',
                'description': 'Corporate training (leadership, HR, strategy execution) - Workshops & seminars',
                'detailed_description': 'Comprehensive training and capacity building programs including corporate training on leadership, HR, strategy, and specialized workshops.',
                'icon': 'ri-graduation-cap-line',
                'hourly_rate': 110,
                'display_order': 5,
                'is_active': True,
                'features': 'Leadership training\nHR workshops\nStrategy execution training\nCustom seminars\nCapacity building programs',
            },
            {
                'name': 'Academic Consultancy',
                'consultancy_type': 'academic',
                'description': 'Expert guidance on academic career planning and research direction',
                'detailed_description': 'One-on-one consultancy with experienced academics to guide your research direction, academic career planning, and publication strategy.',
                'icon': 'ri-discuss-line',
                'hourly_rate': 100,
                'display_order': 6,
                'is_active': True,
                'features': 'Academic career planning\nResearch direction guidance\nPublication strategy\nCareer development coaching',
            },
            {
                'name': 'Research Methodology Consultancy',
                'consultancy_type': 'research',
                'description': 'Specialized guidance on research methods and approaches',
                'detailed_description': 'Expert consultation on selecting and implementing appropriate research methodologies for your specific research questions.',
                'icon': 'ri-compass-line',
                'hourly_rate': 120,
                'display_order': 7,
                'is_active': True,
                'features': 'Research methodology selection\nSampling strategy\nHypothesis development\nResearch design guidance',
            },
            {
                'name': 'Career Development Consultancy',
                'consultancy_type': 'career',
                'description': 'Personalized career guidance for academic and professional growth',
                'detailed_description': 'Professional coaching to develop your academic and professional career strategy, publication roadmap, and professional networking.',
                'icon': 'ri-briefcase-line',
                'hourly_rate': 90,
                'display_order': 8,
                'is_active': True,
                'features': 'Career strategy development\nPublication roadmap\nProfessional networking\nCareer coaching',
            },
            {
                'name': 'Academic Writing Consultancy',
                'consultancy_type': 'writing',
                'description': 'One-on-one guidance for improving academic writing skills',
                'detailed_description': 'Personalized writing consultancy to improve clarity, structure, and academic tone in your research papers and dissertations.',
                'icon': 'ri-edit-line',
                'hourly_rate': 85,
                'display_order': 9,
                'is_active': True,
                'features': 'Writing skills coaching\nManuscript review\nStructure and clarity improvement\nAcademic tone guidance',
            },
        ]
        
        services = []
        for service_data in consultancy_data:
            service, created = ConsultancySubService.objects.get_or_create(
                name=service_data['name'],
                defaults=service_data,
            )
            services.append(service)
        
        self.stdout.write(f'✓ Created {len(services)} consultancy services')
        return ConsultancySubService.objects.filter(is_active=True)

    def _create_workshops(self):
        """Create sample workshops"""
        now = timezone.now()
        workshops_data = [
            {
                'title': 'Research Paper Writing Masterclass',
                'description': 'Learn the fundamentals of writing compelling research papers',
                'detailed_description': 'This workshop covers the essential elements of research paper writing including structure, literature integration, and academic tone.',
                'date': now + timedelta(days=7),
                'location': 'Virtual Room A',
                'is_online': True,
                'meeting_url': 'https://zoom.us/j/123456789',
                'max_participants': 30,
                'price': 50,
                'is_active': True,
            },
            {
                'title': 'Statistical Analysis with Python',
                'description': 'Advanced statistical methods using Python libraries',
                'detailed_description': 'Hands-on workshop on statistical analysis using Python, including NumPy, Pandas, SciPy, and visualization techniques.',
                'date': now + timedelta(days=14),
                'location': 'Virtual Room B',
                'is_online': True,
                'meeting_url': 'https://zoom.us/j/987654321',
                'max_participants': 25,
                'price': 75,
                'is_active': True,
            },
            {
                'title': 'Thesis Writing & Defense Preparation',
                'description': 'Complete guide to thesis writing and defending',
                'detailed_description': 'Comprehensive workshop covering thesis structure, writing tips, formatting requirements, and defense preparation strategies.',
                'date': now + timedelta(days=21),
                'location': 'Main Campus Hall',
                'is_online': False,
                'max_participants': 50,
                'price': 35,
                'is_active': True,
            },
            {
                'title': 'Literature Review Techniques',
                'description': 'Systematic approaches to conducting literature reviews',
                'detailed_description': 'Learn systematic methods for finding, evaluating, and synthesizing research literature for your research project.',
                'date': now + timedelta(days=28),
                'location': 'Virtual Room C',
                'is_online': True,
                'meeting_url': 'https://zoom.us/j/456789123',
                'max_participants': 40,
                'price': 40,
                'is_active': True,
            },
            {
                'title': 'Academic Research Ethics & Integrity',
                'description': 'Essential guidance on research ethics and academic integrity',
                'detailed_description': 'Workshop on ethical research practices, plagiarism prevention, proper citation, and responsible research conduct.',
                'date': now + timedelta(days=35),
                'location': 'Virtual Room D',
                'is_online': True,
                'meeting_url': 'https://zoom.us/j/789123456',
                'max_participants': 60,
                'price': 25,
                'is_active': True,
            },
        ]
        
        workshops = []
        for workshop_data in workshops_data:
            workshop, created = Workshop.objects.get_or_create(
                title=workshop_data['title'],
                defaults=workshop_data,
            )
            workshops.append(workshop)
        
        self.stdout.write(f'✓ Created {len(workshops)} workshops')
        return workshops

    def _create_service_requests(self, users, services):
        """Create sample service requests"""
        service_list = list(services)
        requests = []
        
        statuses = ['pending', 'accepted', 'in_progress', 'completed', 'completed']
        now = timezone.now()
        
        for i, user in enumerate(users):
            customer = user.customer_profile
            service = service_list[i % len(service_list)]
            status = statuses[i % len(statuses)]
            
            request_obj, created = ServiceRequest.objects.get_or_create(
                customer=customer,
                service=service,
                defaults={
                    'title': f'{service.name} - Project {i+1}',
                    'description': f'Requesting professional {service.name.lower()} services for my academic project.',
                    'status': status,
                    'deadline': now + timedelta(days=14),
                    'budget': 1500 + (i * 200),
                    'created_at': now - timedelta(days=7-i),
                    'completed_at': now if status == 'completed' else None,
                }
            )
            if created:
                requests.append(request_obj)
        
        self.stdout.write(f'✓ Created {len(requests)} service requests')
        return ServiceRequest.objects.all()

    def _create_testimonials(self, users, services):
        """Create sample testimonials"""
        service_list = list(services)
        testimonials = []
        
        testimonial_quotes = [
            'Excellent service! The work was completed professionally and on time.',
            'Very satisfied with the quality and attention to detail.',
            'Highly recommended! Great communication throughout the process.',
            'Outstanding results. The team really understood my requirements.',
            'Impressive work. Will definitely use again for future projects.',
            'Professional and reliable. Exceeded my expectations.',
            'Great support and high-quality deliverables.',
            'Best service I have used for academic work.',
        ]
        
        for i, user in enumerate(users):
            customer = user.customer_profile
            service = service_list[i % len(service_list)]
            
            testimonial, created = ClientTestimonial.objects.get_or_create(
                customer=customer,
                service=service,
                defaults={
                    'rating': 5 - (i % 2),  # Mix of 4 and 5 star reviews
                    'quote': testimonial_quotes[i % len(testimonial_quotes)],
                    'is_published': True,
                    'is_featured': i < 3,  # Feature first 3
                    'created_at': timezone.now() - timedelta(days=30-i),
                }
            )
            if created:
                testimonials.append(testimonial)
        
        self.stdout.write(f'✓ Created {len(testimonials)} testimonials')
        return testimonials
