**Purpose**
- Offers research and academic writing services, consultancy, and training with rich content (images, videos, FAQs, testimonials, workshops).
- Lets clients explore services, submit requests, and contact/consult with the team.
- Provides a custom admin to manage all content (services, media, FAQs, leadership, requests, workshops, reports).

**Core Entities**
- `Customer`: links to `User`, stores contact info and type.
- `ResearchService`: service catalog item with category, pricing, turnaround, and relations to media/FAQs.
- `ConsultancySubService`: consultancy items with features list and pricing.
- `ServiceImage`: images per service; supports `is_featured` and `display_order`.
- `TutorialVideo`: tutorial content per service; supports `video_file` upload and optional `video_url`, `duration`, `display_order`, `is_published`.
- `ServiceFAQ`: FAQs per service; `display_order`, `is_published`.
- `ClientTestimonial`: ratings and quotes linked to `Customer` and optional `ResearchService`.
- `Workshop` and `WorkshopRegistration`: events and registrations; online/offline support and capacity tracking.
- `Leadership`: team members with photos, titles, social links, `display_order`.
- `ServiceRequest`: requests lifecycle (`pending`, `accepted`, `in_progress`, `completed`, `cancelled`); optional attachment path saved in `notes`.
- `CompanyProfile` and `Notification`: company settings and user notifications.

**Pages**
- **Services**
  - Sections
    - Academic Writing Services: lists active `ResearchService` with categories like `thesis`, `articles`, `data_analysis`, `research_design`.
    - Training & Capacity Building: lists `ResearchService` with `category='training_capacity'`.
    - Consultancy and Workshops are linked but primary focus is Academic and Training blocks.
  - Content per service
    - Featured image using `ServiceImage` with `is_featured`; fallback to category default if none.
    - Tutorial videos grid:
      - Inline `<video>` when `video_file` exists (`{{ video.video_file.url }}`).
      - Modal opener when only `video_url` exists (YouTube/embed).
      - Shows `title` and optional `duration`.
    - FAQs accordion:
      - Lists published `ServiceFAQ` ordered by `display_order`.
      - Toggle open/close behavior.
  - Actions
    - “View Details” link to `service_detail` for deep content.
    - Quick Enquiry modal (name, email, message; assigned `service_id`).
    - Consultation form (AJAX) with fields: `name`, `email`, `phone` (optional), `service_type`, `message`, `attachment` (optional).
      - Submits to `api/submit-consultation/` (URL name `submit_consultation`).
      - Creates a `ServiceRequest` and stores attachment path in `notes`.
  - Enhancements
    - Animated counters, category tabs, sliders (testimonials), back-to-top, file attachment UI.
- **Service Detail**
  - Displays `ResearchService` description, detailed description, pricing/turnaround, related services.
  - Media sections:
    - Featured and gallery images from `ServiceImage`.
    - Tutorial videos with the same file-vs-URL logic; plays inline for uploaded files.
  - Social proof:
    - `ClientTestimonial` list filtered by service; published only.
  - Action: “Request Service” form for authenticated users, creates `ServiceRequest`.
- **Contact**
  - Traditional POST form with fields: `full_name`, `email`, `phone` (optional), `service` (select from active services), `subject`, `message`.
  - On submit:
    - Finds or creates `Customer` by `email`.
    - Creates `ServiceRequest` with optional `service`.
    - Shows success message and redirects.
- **About**
  - Company overview using `CompanyProfile`: vision, mission, story, contact and social links.
  - Stats: counts of active services, consultancy entries, customers, completed requests.
  - Leadership section: `Leadership` members sorted by `display_order` with photo, title, affiliation, bio, social links.
- **Workshops**
  - Lists upcoming `Workshop` entries; shows date, location/online status, price, registration counts, capacity.
  - Links to detail/register flow (if implemented in your app).
- **Custom Admin**
  - Navigation in `admin/base.html` with sidebar links:
    - `admin_services`, `admin_consultancy`, `admin_service_images`, `admin_tutorial_videos`, `admin_faqs`, `admin_requests`, `admin_workshops`, `admin_leadership`, `admin_reports`.
  - Pages provide full action buttons:
    - Services: create/delete.
    - Consultancy: create/update/delete; manage features.
    - Service Images: upload; toggle `is_featured`; delete.
    - Tutorial Videos: upload `video_file` or add `video_url`; toggle `is_published`; delete.
    - Service FAQs: add/edit Q/A; toggle `is_published`; delete.
    - Requests: accept/complete/cancel.
    - Workshops: create/schedule/manage registrations.
    - Leadership: create/edit order and visibility.
    - Reports: aggregate stats.

**Endpoints**
- Frontend
  - `services` → builds context of services, images, videos, FAQs for listings.
  - `service_detail/<id>` → detailed page per service.
  - `contact` → POST handles contact form, creates `ServiceRequest`.
  - `service_request/<id>` → authenticated request creation for a service.
- Admin (staff)
  - `admin/services`, `admin/consultancy`, `admin/images`, `admin/tutorials`, `admin/faqs`, `admin/requests`, `admin/workshops`, `admin/leadership`, `admin/reports`.
- API
  - `api/get-services` → list active services JSON.
  - `api/get-testimonials` → latest published testimonials JSON.
  - `api/get-workshops` → upcoming workshops JSON.
  - `api/submit-contact` → JSON contact submission based on `ContactForm`.
  - `api/submit-consultation` (`submit_consultation`) → FormData consultation submission; returns JSON.

**Data Population**
- Command `populate_sample_data`:
  - Seeds admin user, sample users.
  - Creates research services (academic) and training services (8+ entries).
  - Creates consultancy sub-services.
  - Adds workshops (online/offline) with dates and prices.
  - Creates service requests and testimonials.
  - For every active `ResearchService` (including training):
    - Adds 3 images (featured + 2 gallery).
    - Adds 4 tutorial videos (YouTube URLs).
    - Adds 4 FAQs (including training-related Qs).
- Run:
  - `cd c:\New folder\new\nowweb12`
  - `python manage.py populate_sample_data` (or use venv `.\tracker\venv\Scripts\python.exe`)

**Media Handling**
- `ServiceImage.image` stored under `media/services/`; featured image used on listings and detail.
- `TutorialVideo.video_file` stored under `media/tutorials/`; inline playback via `<video>`.
- `TutorialVideo.video_url` supported for external content; opens modal in listings and detail.
- Consultation attachments saved to `media/consultations/`; path recorded in `ServiceRequest.notes`.

**Security & Flow**
- Admin views require `login_required` and `is_staff`.
- `service_request` requires authentication; contact and consultation can create `Customer` implicitly.
- Forms include CSRF protection; AJAX endpoints accept JSON or FormData per contract.

**URL Names & Contracts**
- Use URL names in templates: `service_detail`, `services`, `contact`, `submit_consultation`, admin names like `admin_service_images`, `admin_tutorial_videos`, `admin_faqs`.
- Ensure reversals in templates match `urls.py` names to avoid `NoReverseMatch`.

**Acceptance Criteria**
- Services page:
  - Academic and Training lists populated from database.
  - Featured images show; fallback to category defaults when missing.
  - Tutorial videos: inline playback for uploaded files; modal for URLs.
  - FAQs accordion shows published items in order.
  - Consultation form submits via AJAX, returns success JSON, handles optional file.
- Service detail:
  - Shows images, videos, FAQs, testimonials; related services; request action works.
- Contact:
  - Form submits and creates a `ServiceRequest`; optional service selection persists; success message appears.
- Admin:
  - All CRUD/toggle actions function; uploads persist; status changes reflect in frontend.
- Workshops:
  - Upcoming list displays correct status and counts.

**Non-Functional**
- Configure `MEDIA_ROOT` and `MEDIA_URL`; serve static and media in development.
- Use clean display orders and consistent icons (`remixicon` names like `ri-file-text-line`, `ri-video-line`).
- Accessibility: add labels/alt text; ensure keyboard navigability for modals and accordions.
- Performance: paginate large lists if needed; compress images; ensure video formats compatible across browsers.

This specification captures the full intent and current behavior of your app, with page-level feature details (about, contact, services) and the surrounding admin/API/contracts. Hand this to any AI or developer to implement a complete, correct, and working application that matches your expected content and flows.

about this app,About The Writing Hub Tz
Empowering Excellence Through Professional Writing and Consultancy Services

Our Story
The Writing Hub Tz is a multinational company engaged in providing academic, research, and business facilitation services. We have served various clients ranging from individual to organizations from various countries. We deliver results that exceed our clients' expectations, and we are committed to providing the highest level of customer service.

Our expertise spans academic writing, consultancy services, research support, and professional development through workshops and training programs designed to help our clients achieve excellence in their respective fields.

Our Impact
1000+
Satisfied Clients

500+
Projects Completed

15+
Service Categories

99%
Client Satisfaction

Our Vision & Mission
Our Vision
To be the leading catalyst for academic, research and professional success by fostering exceptional writing skills and promoting impactful communication.

Our Mission
To provide comprehensive writing solutions and support for academic, research and business communities., The Writing Hub Tz
Empowering excellence through professional writing, research, and consultancy services for academic and business success.

Quick Links
Home
Services
About Us
Contact
Login
Contact Info
 thewritinghubtz@gmail.com

 +255 717 313 797

 9 Floor, Elite Towers
Azikiwe St, Dar es Salaam
Tanzania

Legal
Privacy Policy
Terms of Service
Cookie Policy
Refund Policy,Get In Touch
Have questions about our services? We're here to help. Fill out the form below or contact us directly.

Full Name
Email
Phone (Optional)
Service of Interest

Select a service...
Subject
Message

Send Message
Contact Information
 Phone
+255 717 313 797

Available 9 AM - 6 PM EAT

 Email
thewritinghubtz@gmail.com

Response within 24 hours

 Address
9 Floor, Elite Towers

Azikiwe St, Dar es Salaam, Tanzania

 Business Hours
Monday - Friday: 9 AM - 6 PM
Saturday: 10 AM - 4 PM
Sunday: Closed
Quick Answers
How long does a typical project take?
Project duration varies based on scope. We discuss timelines during our consultation.

What's your revision policy?
We offer unlimited revisions until you're completely satisfied with the work.

Do you offer rush services?
Yes! Contact us to discuss rush deadlines and pricing.

Visit Us - Find Our Location
The Writing Hub TZ
9 Floor, Elite Towers
Azikiwe Street
Dar es Salaam, Tanzania
+255 717 313 797
×
+
−
 Leaflet | © OpenStreetMap contributors
Address
9 Floor, Elite Towers
Azikiwe St, Dar es Salaam, Tanzania
Phone
+255 717 313 797
Hours
Mon-Fri: 9 AM - 6 PM
Sat: 10 AM - 4 PM
 Open in Google Maps
 The Writing Hub Tz
Empowering excellence through professional writing, research, and consultancy services for academic and business success.

Quick Links
Home
Services
About Us
Contact
Login
Contact Info
 thewritinghubtz@gmail.com

 +255 717 313 797

 9 Floor, Elite Towers
Azikiwe St, Dar es Salaam
Tanzania

Legal
Privacy Policy
Terms of Service
Cookie Policy
Refund Policy
© 2024 The Writing Hub Tz. All rights reserved.

Empowering Excellence Through Wo(the contact page contain real map section)
