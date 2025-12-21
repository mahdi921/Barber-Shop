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

## 🔗 Make.com Webhook Integration

The system includes a production-ready webhook integration that sends appointment notifications to Make.com (formerly Integromat) for downstream automation workflows.

### Features

- **Dual Webhook Events**: Sends webhooks both when appointment is created (`pending`) and when confirmed
- **Reliable Delivery**: Asynchronous Celery tasks with exponential backoff retry (max 5 attempts)
- **HMAC Security**: Signed payloads with SHA256 signature for verification
- **Idempotency**: Each webhook has a unique key to prevent duplicate processing
- **Full Audit Trail**: All delivery attempts tracked in database with response codes
- **Admin Interface**: View, retry, and resend webhooks via Django admin
- **Fallback Mode**: If no webhook URL configured, payloads stored as 'pending' for later processing

### Configuration

Add these environment variables to your `.env` file:

```bash
# Make.com Webhook Integration
MAKE_WEBHOOK_URL=https://hook.make.com/your-webhook-id-here
MAKE_WEBHOOK_SECRET=your-secret-key-for-hmac-signature
```

**Note**: If `MAKE_WEBHOOK_URL` is left empty, webhooks will be queued but marked as 'pending' in the database for manual processing later.

### Webhook Payload

Each webhook POST includes:

**Headers:**
- `Content-Type: application/json`
- `Idempotency-Key: appointment:{id}:{event_type}` - Unique key for deduplication
- `X-Make-Signature: sha256={hex_digest}` - HMAC signature for verification

**Body Example:**

```json
{
  "appointment_id": "123e4567-e89b-12d3-a456-426614174000",
  "event_type": "created",
  "created_at": "2025-12-21T08:18:00Z",
  "customer": {
    "id": 42,
    "phone": "0912***5678",
    "first_name": "علی",
    "last_name": "محمدی"
  },
  "salon": {
    "id": 5,
    "name": "آرایشگاه مدرن",
    "address": "تهران، خیابان ولیعصر"
  },
  "stylist": {
    "id": 12,
    "name": "رضا احمدی"
  },
  "services": [{
    "id": 7,
    "name": "کوتاهی مو مردانه",
    "price": "150000",
    "duration_minutes": 30
  }],
  "total_price": "150000",
  "total_duration_minutes": 30,
  "appointment_start": "2025-12-22T14:00:00+03:30",
  "appointment_end": "2025-12-22T14:30:00+03:30",
  "status": "pending",
  "metadata": {
    "is_first_time_customer": false,
    "source": "web",
    "persian_date": "1404/10/01"
  }
}
```

Full example payload: [`docs/webhook_payload_example.json`](docs/webhook_payload_example.json)

### Signature Verification

To verify the webhook signature in Make.com:

```javascript
// In Make.com HTTP module
const crypto = require('crypto');
const bodyString = JSON.stringify(request.body);
const secret = 'your-secret-key';
const signature = crypto
  .createHmac('sha256', secret)
  .update(bodyString)
  .digest('hex');

const receivedSig = request.headers['x-make-signature'].replace('sha256=', '');

if (signature === receivedSig) {
  // Signature valid, process webhook
} else {
  // Invalid signature, reject
}
```

### Retry Policy

- **Transient Errors (5xx)**: Automatic retry with exponential backoff
  - Retry 1: 60s delay
  - Retry 2: 120s delay
  - Retry 3: 240s delay
  - Retry 4: 480s delay
  - Retry 5: 960s delay (max)
  
- **Permanent Errors (4xx)**: No retry, marked as 'failed'

- **Network Errors**: Retry with exponential backoff

### Admin Interface

Access webhook deliveries in Django admin:

1. Navigate to **Webhook Deliveries** in admin panel
2. View all delivery attempts with status, response codes, and payloads
3. **Retry Failed**: Select failed deliveries and use "Retry Failed Webhooks" action
4. **Resend**: Select any delivery and use "Resend Webhooks" action

### Management Commands

**Retry a specific failed webhook:**

```bash
docker-compose exec backend python manage.py retry_webhook <delivery_id>
```

**Resend webhook for an appointment:**

```bash
# Resend 'created' event
docker-compose exec backend python manage.py resend_appointment_webhook <appointment_id>

# Resend 'confirmed' event
docker-compose exec backend python manage.py resend_appointment_webhook <appointment_id> --event-type confirmed
```

### Local Testing

**1. Start the mock webhook server:**

```bash
# Install Flask first
pip install flask

# Run mock server
python scripts/mock_make_webhook.py
```

The mock server will listen on `http://localhost:8001/webhook` and display received webhooks in the terminal.

**2. Configure local webhook URL:**

```bash
# In .env file
MAKE_WEBHOOK_URL=http://localhost:8001/webhook
MAKE_WEBHOOK_SECRET=test-secret-key
```

**3. Create a test appointment:**

```bash
# Via Django shell
docker-compose exec backend python manage.py shell

>>> from apps.appointments.models import Appointment
>>> # Create appointment and it will trigger webhook automatically
```

**4. Verify delivery:**

Check the mock server terminal output to see the received webhook with full payload details.

**Manual curl test:**

```bash
# Compute signature and send test webhook
BODY='{"test":"data"}'
SECRET="test-secret-key"
SIGNATURE=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)

curl -X POST http://localhost:8001/webhook \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: test-key-123" \
  -H "X-Make-Signature: sha256=$SIGNATURE" \
  -d "$BODY"
```

### Troubleshooting

**Webhook not sending:**

1. Check Celery worker is running: `docker-compose logs worker`
2. Verify `MAKE_WEBHOOK_URL` is set in `.env`
3. Check Redis connection: `docker-compose exec redis redis-cli ping`
4. View webhook delivery records in Django admin

**Signature verification failing:**

1. Ensure `MAKE_WEBHOOK_SECRET` matches on both sides
2. Verify you're computing HMAC on the raw request body (not parsed JSON)
3. Check signature header format: `sha256=<hex_digest>`

**Webhooks marked as 'failed':**

1. Check Make.com webhook endpoint is accessible
2. Review error message in WebhookDelivery admin
3. Retry manually via admin action or management command

### Database Models

**WebhookDelivery fields:**
- `appointment` - ForeignKey to Appointment
- `event_type` - 'created' or 'confirmed'
- `payload` - JSONField with full webhook payload
- `status` - queued, sending, sent, failed, pending
- `idempotency_key` - Unique key
- `attempts_count` - Number of delivery attempts
- `response_code` - HTTP response code
- `response_body` - Response from Make.com
- `error_message` - Error details if failed

**Appointment webhook fields:**
- `webhook_created_sent` - Boolean, if 'created' webhook sent
- `webhook_confirmed_sent` - Boolean, if 'confirmed' webhook sent

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
