# سیستم رزرو سالن آرایشگری / Barber Shop Booking System

A comprehensive Persian-language salon booking platform built with Django 5.2, PostgreSQL, Redis, and Docker.

## 🌟 Features

- **Multi-role Authentication**: Custom phone-based authentication for customers, salon managers, stylists, and site admins
- **CAPTCHA Protection**: Bot prevention on registration and login
- **Salon Manager Approval**: Admin approval workflow for new salon registrations
- **Gender-based Filtering**: Male customers see only male salons, female customers see only female salons
- **Jalali Calendar**: Full Persian calendar support for appointments
- **Anonymous Ratings**: Customers rate stylists anonymously (1-5 stars)
- **Temporary Stylist Accounts**: Salon managers create temporary stylists who complete profiles on first login
- **Redis Caching**: Cached salon lists, ratings, and availability
- **Responsive Persian UI**: Vazirmatn font, RTL layout, Bootstrap

## 📋 Requirements

- Docker & Docker Compose
- Python 3.13+
- PostgreSQL (alpine)
- Redis (alpine)

## 🚀 Quick Start

### 1. Clone and Setup Environment

```bash
cd /home/mahdi/Projects/Barber-Shop

# Copy environment file
cp .env.example .env

# Edit .env and set your SECRET_KEY and database password
nano .env
```

### 2. Build and Run with Docker

```bash
# Build containers (development environment)
docker-compose build

# Start services
docker-compose up -d

# Check services are running
docker-compose ps
```

### 3. Run Migrations

```bash
# Run database migrations
docker-compose exec web python manage.py migrate

# Create superuser (site admin)
docker-compose exec web python manage.py createsuperuser
# Enter Iranian phone number (e.g., 09123456789) and password
```

### 4. Collect Static Files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 5. Access the Application

- **Main site**: http://localhost:8000
- **Admin panel**: http://localhost:8000/admin
- **API**: http://localhost:8000/accounts/api/

## 🏗️ Project Structure

```
Barber-Shop/
├── config/                  # Django settings
│   ├── settings.py         # Main configuration
│   ├── urls.py             # URL routing
│   └── celery.py           # Async tasks
├── apps/
│   ├── accounts/           # User authentication & profiles
│   ├── salons/             # Salon & service management
│   ├── appointments/       # Booking system
│   ├── ratings/            # Ratings & reviews
│   └── core/               # Shared utilities
├── templates/              # HTML templates (Persian UI)
├── static/                 # Static files (CSS, JS)
├── media/                  # User uploads
├── docker-compose.yml      # Container orchestration
├── Dockerfile              # Multi-stage build
└── requirements.txt        # Python dependencies
```

## 👥 User Roles

### Customer
- Register with: phone, name, selfie, gender, DOB
- View salons matching their gender
- Book appointments with stylists
- Rate and review services anonymously
- View own submitted reviews

### Salon Manager
- Register with: phone, salon name/photo/address, salon gender
- **Requires approval by site admin**
- Add temporary stylists by phone number
- Define services and prices
- Set working hours for salon/stylists
- View and manage appointments
- Cannot edit ratings/reviews

### Stylist
- Created by salon manager as "temporary"
- Complete profile on first login (name, gender, DOB)
- View own ratings and reviews (read-only)
- Set working schedule
- Define offered services

### Site Admin
- Approve/reject salon manager registrations
- Manage all users and entities
- Full system access via Django admin

## ⚙️ Core Workflows

### 1. Salon Manager Registration & Approval

```bash
# User registers as salon manager
POST /accounts/register/manager/

# Admin approves in Django admin or via API
POST /accounts/api/approve-manager/<id>/

# Manager can now login and operate
```

### 2. Adding Temporary Stylists

Salon managers add stylists by phone number. The stylist is created with `is_temporary=True` and must complete their profile on first login.

```python
# In salon manager dashboard
stylist = StylistProfile.objects.create(
    user=CustomUser.objects.create_user(phone_number='09XXXXXXXXX', password='temp123', user_type='stylist'),
    salon=manager.salon,
    is_temporary=True
)

# On stylist's first login, middleware redirects to completion page
```

### 3. Booking Appointment

```bash
# Customer views available slots (Jalali calendar)
GET /appointments/api/availability/?stylist_id=1&date=1402/09/15

# Customer books appointment
POST /appointments/api/book/
{
    "stylist_id": 1,
    "service_id": 2,
    "jalali_date": "1402/09/20",
    "time_slot": "14:00"
}
```

### 4. Rating After Service Completion

```bash
# After appointment status = 'completed'
POST /ratings/api/submit/
{
    "appointment_id": 10,
    "rating": 5,
    "review_text": "عالی بود!"
}
```

## 🗄️ Database Schema

### Key Models

- **CustomUser**: Phone-based auth, user_type field
- **CustomerProfile**: One-to-one with user, stores personal info
- **SalonManagerProfile**: Site, approval status
- **StylistProfile**: Temporary flag, profile completion
- **Salon**: Gender type, cached rating
- **Service**: Gender-specific service types
- **Appointment**: Unique constraint prevents double-booking
- **Rating & Review**: Anonymous display, linked to customer for "my reviews"

### Important Constraints

```sql
-- Prevent double-booking
UNIQUE (stylist, appointment_date, appointment_time) WHERE status IN ('pending', 'confirmed')

-- One rating per appointment
UNIQUE (customer, appointment)
```

## 🔒 Security Features

1. **Phone Validation**: Iranian format (09XXXXXXXXX)
2. **CAPTCHA**: On registration and login
3. **Role-based Permissions**: DRF custom permissions
4. **Transaction-based Booking**: Prevents race conditions
5. **Password Hashing**: Django PBKDF2
6. **File Upload Validation**: Image type and size limits

## 📊 Caching Strategy

### Cached Data

- **Salon Lists**: `salon_list:gender:{gender}:approved` (5 min TTL)
- **Stylist Availability**: `availability:stylist:{id}:date:{date}` (5 min TTL)
- **Salon Ratings**: `salon_rating:{salon_id}` (10 min TTL)

### Cache Invalidation

Automatic via Django signals when:
- New rating submitted → invalidate stylist + salon rating cache
- Schedule updated → invalidate availability cache
- Salon approved → invalidate salon list cache

## 🧪 Testing

### Run Tests

```bash
# All tests
docker-compose exec web python manage.py test

# Specific app
docker-compose exec web python manage.py test apps.accounts
docker-compose exec web python manage.py test apps.appointments

# With coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
docker-compose exec web coverage html
```

### Test Categories

1. **accounts/tests.py**
   - User registration with valid/invalid phone
   - Salon manager approval workflow
   - Temporary stylist completion
   - Login with CAPTCHA

2. **appointments/tests.py**
   - Double-booking prevention
   - Jalali date conversion
   - Availability calculation
   - Gender-based salon filtering

3. **ratings/tests.py**
   - Anonymous rating display
   - Salon rating aggregation
   - Customer "my reviews" view
   - One rating per appointment constraint

## 🌐 API Endpoints

### Authentication

```
POST /accounts/api/register/customer/
POST /accounts/api/register/manager/
POST /accounts/api/stylist/complete-profile/
GET  /accounts/api/me/
```

### Admin Actions

```
GET  /accounts/api/pending-managers/
POST /accounts/api/approve-manager/<id>/
```

### Salons (to be implemented)

```
GET  /salons/api/list/
GET  /salons/api/detail/<id>/
POST /salons/api/add-stylist/
```

### Appointments (to be implemented)

```
GET  /appointments/api/availability/
POST /appointments/api/book/
GET  /appointments/api/my-appointments/
```

### Ratings (to be implemented)

```
POST /ratings/api/submit/
GET  /ratings/api/stylist/<id>/
GET  /ratings/api/my-reviews/
```

## 🛠️ Development

### Create Custom Management Commands

```bash
# Example: Seed database with sample data
docker-compose exec web python manage.py seed_data
```

### Run Development Server

```bash
# Hot-reload enabled
docker-compose up
```

### View Logs

```bash
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f redis
```

## 🚢 Deployment

### Staging Environment

```bash
# Build staging image
docker-compose build --build-arg TARGET=staging

# Deploy
docker-compose -f docker-compose.staging.yml up -d
```

### Production Environment

```bash
# Build production image
docker build --target production -t salon-booking:prod .

# Run with production settings
docker-compose -f docker-compose.prod.yml up -d

# Important: Set DEBUG=False in .env
# Important: Set strong SECRET_KEY
# Important: Configure ALLOWED_HOSTS
```

### Environment Variables (Production)

```bash
DEBUG=False
SECRET_KEY=<strong-random-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
POSTGRES_PASSWORD=<strong-db-password>
CELERY_BROKER_URL=redis://redis:6379/0
```

## 📱 SMS Integration (Optional)

The system includes SMS stubs for future integration:

```python
# In apps/core/sms.py
# Integrate with Kavenegar, Ghasedak, or other Iranian SMS providers

SMS_PROVIDER = 'kavenegar'  # Change in settings
SMS_API_KEY = 'your-api-key'
```

## 🗓️ Jalali Calendar Widget

Frontend integration example:

```html
<!-- Include Persian Date Picker -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/persian-datepicker@latest/dist/css/persian-datepicker.min.css">
<script src="https://cdn.jsdelivr.net/npm/persian-datepicker@latest/dist/js/persian-datepicker.min.js"></script>

<input type="text" id="appointment-date" class="jalali-picker">

<script>
$('#appointment-date').persianDatepicker({
    format: 'YYYY/MM/DD',
    initialValue: false,
    autoClose: true
});
</script>
```

## 🤝 Contributing

1. Create feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Submit pull request

## 📄 License

All rights reserved © 2024

## 🆘 Troubleshooting

### Database Connection Error

```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database
docker-compose restart db

# Check logs
docker-compose logs db
```

### Redis Connection Error

```bash
# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

### Migration Issues

```bash
# Reset migrations (CAUTION: deletes data)
docker-compose exec web python manage.py migrate <app> zero
docker-compose exec web python manage.py migrate
```

### Permission Denied on Media Files

```bash
# Fix permissions
docker-compose exec web chown -R appuser:appuser /app/media
```

## 📞 Support

For questions or issues, contact the development team.

---

**تمامی حقوق محفوظ است © 1402**
