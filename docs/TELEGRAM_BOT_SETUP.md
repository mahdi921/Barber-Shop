# Telegram Bot Setup Guide

Quick guide to set up the Telegram bot for appointment notifications.

---

## 🤖 Step 1: Create Bot with @BotFather

1. Open Telegram and search for **@BotFather**
2. Start a chat and send `/newbot`
3. **Bot Name**: Enter a display name (e.g., "آرایشگاه نوین")
4. **Username**: Enter a unique username ending in 'bot' (e.g., `BarberShopNovinBot`)
5. **Copy the bot token** provided by BotFather (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

---

## 🔧 Step 2: Configure Django

Add the bot token to your `.env` file:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

---

## 💾 Step 3: Run Database Migration

Apply the migration to add `telegram_chat_id` field:

```bash
docker-compose exec web python manage.py migrate accounts
```

Expected output:
```
Applying accounts.0004_customerprofile_telegram_chat_id... OK
```

---

## 🚀 Step 4: Start the Telegram Bot

### Option A: Run Locally (Development)

```bash
# Install dependencies first
docker-compose exec web pip install python-telegram-bot

# Run the bot
docker-compose exec web python telegram_bot.py
```

### Option B: Docker Service (Production)

Add to `docker-compose.yml`:

```yaml
services:
  # ... existing services ...
  
  telegram-bot:
    build: .
    command: python telegram_bot.py
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
    depends_on:
      - db
      - redis
    restart: unless-stopped
```

Then:
```bash
docker-compose up -d telegram-bot
```

---

## 📱 Step 5: Customer Links Their Account

Customers need to:

1. **Find your bot** in Telegram (search for `BarberShopNovinBot` or whatever username you chose)
2. **Start the bot** with their phone number:
   ```
   /start 09121234567
   ```
3. **Receive confirmation** message

---

## ✅ Step 6: Test the Integration

### Test Bot Commands:

```
/start 09121234567   # Link account
/status              # Check connection status
/help                # Show help
```

### Test Full Flow:

1. **Customer registers** on website: `http://localhost:5173/register/customer`
2. **Customer starts bot**: `/start 09121234567` in Telegram
3. **Customer books appointment** on website
4. **Django sends webhook** to Make.com
5. **Make.com sends Telegram** message
6. **Customer receives** notification! 🎉

---

## 🔍 Verify Customer Has Telegram Linked

### Via Django Admin:

1. Go to `http://localhost:8000/admin`
2. **Accounts** → **Customer profiles**
3. Click on a customer
4. Check **Telegram chat ID** field - should have a value

### Via Django Shell:

```python
docker-compose exec web python manage.py shell

from apps.accounts.models import CustomerProfile

# Check specific customer
customer = CustomerProfile.objects.get(user__phone_number='09121234567')
print(f"Telegram Chat ID: {customer.telegram_chat_id}")

# List all customers with Telegram
linked = CustomerProfile.objects.exclude(telegram_chat_id__isnull=True)
for c in linked:
    print(f"{c.full_name}: {c.telegram_chat_id}")
```

---

## 🔧 Bot Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `/start <phone>` | Link Telegram account | `/start 09121234567` |
| `/status` | Check link status | `/status` |
| `/help` | Show help message | `/help` |

---

## 🐛 Troubleshooting

### Bot doesn't respond:

✅ **Check bot token** is correct in `.env`  
✅ **Check bot process** is running: `docker-compose logs telegram-bot`  
✅ **Test bot** in Telegram with @BotFather's `/mybots` → Test Bot

### Customer can't link account:

✅ **Phone format** must be `09XXXXXXXXX` (11 digits)  
✅ **Customer must exist** in database (registered on website)  
✅ **Phone must match** exactly with website registration

### Telegram messages not received:

✅ **Customer linked account?** Check with `/status`  
✅ **Webhook configured?** Check `MAKE_WEBHOOK_URL` in `.env`  
✅ **Make.com running?** Check execution history  
✅ **Check logs**: `docker-compose logs web`

---

## 📊 Monitoring

### Check Bot Statistics:

```bash
# View bot logs
docker-compose logs -f telegram-bot

# Check how many customers linked
docker-compose exec web python manage.py shell
>>> from apps.accounts.models import CustomerProfile
>>> CustomerProfile.objects.exclude(telegram_chat_id__isnull=True).count()
```

### Test Notification Manually:

```python
docker-compose exec web python manage.py shell

from apps.appointments.tasks import deliver_appointment_webhook
from apps.appointments.models import Appointment

# Get an appointment
appt = Appointment.objects.first()

# Trigger webhook manually
deliver_appointment_webhook(str(appt.id), 'created')
```

Then check Make.com execution history and Telegram!

---

## 🎨 Customize Bot Messages

Edit messages in `telegram_bot.py`:

- **/start success message**: Line ~97
- **/start help message**: Line ~111
- **/status linked message**: Line ~130
- **/help message**: Line ~150

After editing, restart the bot:
```bash
docker-compose restart telegram-bot
```

---

## 🔐 Security Notes

1. **Never share** your bot token publicly
2. **Keep token** in `.env` file (not in git)
3. **Bot validates** phone numbers before linking
4. **One phone** = One Telegram account (enforced by unique constraint)

---

## 🚀 Production Deployment

For production:

1. **Use systemd or docker-compose** to ensure bot always runs
2. **Monitor bot health** with process manager
3. **Set up alerts** for bot downtime
4. **Log all link attempts** for security audit
5. **Consider rate limiting** for `/start` command

---

## 📞 Support

If customers need help:

1. **Check bot is running**: `docker-compose ps telegram-bot`
2. **Review logs**: `docker-compose logs telegram-bot --tail 100`
3. **Test with your own account** first
4. **Provide clear instructions** in website/app

---

Enjoy automated Telegram notifications! 🎊
