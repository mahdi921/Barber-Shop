# Make.com Webhook Integration - Quick Reference

## 📁 All Files Created/Modified

### Core Implementation
1. **[models.py](../../../apps/appointments/models.py)** - Added WebhookDelivery model + Appointment webhook fields
2. **[signals.py](../../../apps/appointments/signals.py)** - NEW: Signal handlers for webhook triggering
3. **[tasks.py](../../../apps/appointments/tasks.py)** - NEW: Celery task for webhook delivery
4. **[apps.py](../../../apps/appointments/apps.py)** - Modified: Import signals on app ready
5. **[admin.py](../../../apps/appointments/admin.py)** - Modified: Added WebhookDelivery admin + updated Appointment admin

### Database
6. **[0002_webhook_integration.py](../../../apps/appointments/migrations/0002_webhook_integration.py)** - NEW: Migration for models

### Management Commands
7. **[retry_webhook.py](../../../apps/appointments/management/commands/retry_webhook.py)** - NEW: Retry command
8. **[resend_appointment_webhook.py](../../../apps/appointments/management/commands/resend_appointment_webhook.py)** - NEW: Resend command

### Configuration
9. **[settings.py](../../../config/settings.py)** - Modified: Added webhook settings
10. **[.env.example](../.env.example)** - Modified: Added webhook env vars
11. **[requirements.txt](../../../requirements.txt)** - Modified: Added requests + responses

### Testing
12. **[test_webhook_integration.py](../../../apps/appointments/tests/test_webhook_integration.py)** - NEW: Comprehensive test suite

### Documentation
13. **[README.md](../../../README.md)** - Modified: Added complete webhook integration section
14. **[webhook_payload_example.json](../../../docs/webhook_payload_example.json)** - NEW: Example payload
15. **[mock_make_webhook.py](../../../scripts/mock_make_webhook.py)** - NEW: Mock webhook server for testing

---

## ⚡ Quick Start Commands

### Apply Migration
```bash
docker-compose exec backend python manage.py migrate
```

### Run Tests
```bash
docker-compose exec backend python manage.py test apps.appointments.tests.test_webhook_integration
```

### Start Mock Server (Local Testing)
```bash
pip install flask
python scripts/mock_make_webhook.py
```

### Management Commands
```bash
# Retry failed webhook
docker-compose exec backend python manage.py retry_webhook <delivery_id>

# Resend webhook for appointment
docker-compose exec backend python manage.py resend_appointment_webhook <appointment_id>
```

---

## 🔧 Configuration

Add to `.env`:
```bash
MAKE_WEBHOOK_URL=https://hook.make.com/your-webhook-id
MAKE_WEBHOOK_SECRET=your-secret-key
```

---

## 📊 Key Models

### WebhookDelivery
- Tracks all webhook delivery attempts
- Fields: status, event_type, payload, response_code, attempts_count
- Admin: View, retry, resend actions

### Appointment (Updated)
- `webhook_created_sent` - Boolean
- `webhook_confirmed_sent` - Boolean

---

## 🎯 Webhook Events

1. **'created'** - Sent when appointment is created (status='pending')
2. **'confirmed'** - Sent when appointment status changes to 'confirmed'

Both events include full appointment, customer, salon, stylist, and service data.

---

## 🔒 Security

- HMAC-SHA256 signature on every webhook
- Header: `X-Make-Signature: sha256=<hex_digest>`
- Phone numbers masked: `0912***4567`
- Idempotency keys: `appointment:{id}:{event_type}`

---

## 📈 Stats

- **Files Created/Modified**: 15
- **Lines of Code**: ~1,500+
- **Test Cases**: 10+
- **Admin Actions**: 2 custom actions
- **Management Commands**: 2 commands
- **Webhook Events**: 2 types
