# Make.com Scenarios for Telegram Notifications

This document provides complete Make.com scenario configurations for sending Telegram notifications when appointments are booked or confirmed.

---

## 🎯 Scenario 1: Basic Telegram Notification (Created Event)

Send a Telegram message when an appointment is created.

### Modules:

#### 1. **Webhooks** → Custom webhook (Trigger)
- **Create a new webhook**
- **Copy the URL** and add to `.env`:
  ```bash
  MAKE_WEBHOOK_URL=https://hook.make.com/abc123xyz
  ```

#### 2. **Router** → Check if customer has Telegram
- **Add Router** after webhook
- **Route 1 - Has Telegram:**
  - **Label**: "Customer has Telegram"
  - **Filter**: 
    ```
    {{1.customer.telegram_chat_id}} Text operator: Is not equal to (empty)
    ```
- **Route 2 - No Telegram:**
  - **Label**: "Skip"
  - No filter (fallback route)

#### 3. **Telegram Bot** → Send a Text Message (on Route 1)
- **Connection**: Add your bot token from @BotFather
- **Chat ID**: 
  ```
  {{1.customer.telegram_chat_id}}
  ```
- **Text**:
  ```
  🎉 نوبت شما با موفقیت ثبت شد!

📋 جزئیات نوبت:
👤 نام: {{1.customer.first_name}} {{1.customer.last_name}}
💈 سالن: {{1.salon.name}}
✂️ آرایشگر: {{1.stylist.name}}

📅 تاریخ: {{1.metadata.persian_date}}
🕐 ساعت: {{formatDate(1.appointment_start; "HH:mm")}}
⏱ مدت: {{1.total_duration_minutes}} دقیقه
💰 هزینه: {{1.total_price}} تومان

📍 آدرس سالن:
{{1.salon.address}}

✅ وضعیت: در انتظار تأیید
🆔 شناسه نوبت: {{1.appointment_id}}

منتظر دیدار شما هستیم! 😊
  ```
- **Parse Mode**: `Markdown` or leave empty

---

## 🎊 Scenario 2: Different Messages for Created/Confirmed

Send different messages based on event type.

### Modules:

#### 1. **Webhooks** → Custom webhook (Trigger)

#### 2. **Router** → Check Telegram + Event Type
- **Route 1 - Created with Telegram:**
  - **Filters**:
    1. `{{1.customer.telegram_chat_id}}` Is not equal to (empty)
    2. AND `{{1.event_type}}` Text operator: Equal to `created`

- **Route 2 - Confirmed with Telegram:**
  - **Filters**:
    1. `{{1.customer.telegram_chat_id}}` Is not equal to (empty)
    2. AND `{{1.event_type}}` Text operator: Equal to `confirmed`

- **Route 3 - No Telegram:**
  - No filter (fallback)

#### 3a. **Telegram Bot** → Send Message (Route 1 - Created)
- **Chat ID**: `{{1.customer.telegram_chat_id}}`
- **Text**:
  ```
📝 نوبت جدید ثبت شد

سلام {{1.customer.first_name}} عزیز!

نوبت شما در سیستم ثبت شد و در انتظار بررسی و تأیید است.

📋 اطلاعات نوبت:
💈 سالن: {{1.salon.name}}
✂️ آرایشگر: {{1.stylist.name}}
📅 تاریخ: {{1.metadata.persian_date}}
🕐 ساعت: {{formatDate(1.appointment_start; "HH:mm")}}

⏳ لطفاً منتظر پیام تأیید بمانید.
🆔 کد پیگیری: {{substring(1.appointment_id; 1; 8)}}
  ```

#### 3b. **Telegram Bot** → Send Message (Route 2 - Confirmed)
- **Chat ID**: `{{1.customer.telegram_chat_id}}`
- **Text**:
  ```
✅ نوبت شما تأیید شد!

تبریک {{1.customer.first_name}}! 🎉

نوبت شما توسط سالن تأیید شده است.

💈 سالن: {{1.salon.name}}
✂️ آرایشگر: {{1.stylist.name}}
📅 تاریخ: {{1.metadata.persian_date}}
🕐 ساعت: {{formatDate(1.appointment_start; "HH:mm")}}
⏱ مدت: {{1.total_duration_minutes}} دقیقه
💰 هزینه: {{1.total_price}} تومان

📍 آدرس:
{{1.salon.address}}

⚠️ لطفاً سر وقت حاضر شوید.

📞 در صورت نیاز به تغییر یا لغو، با سالن تماس بگیرید.
  ```

---

## 💎 Scenario 3: Advanced with Buttons

Send messages with inline keyboard buttons.

#### Telegram Bot → Send a Message
- **Chat ID**: `{{1.customer.telegram_chat_id}}`
- **Text**: (same as above)
- **Reply Markup**: Click "Add item" and select "Inline keyboard"
- **Inline Keyboard**:
  ```json
  [
    [
      {
        "text": "📍 مسیریابی",
        "url": "https://maps.google.com/?q={{1.salon.address}}"
      }
    ],
    [
      {
        "text": "📞 تماس با سالن",
        "url": "tel:+98..."
      },
      {
        "text": "🌐 وبسایت",
        "url": "https://yoursite.com"
      }
    ]
  ]
  ```

**Or use the GUI:**
- **Row 1:**
  - **Button**: Text: "📍 مسیریابی", URL: `https://maps.google.com/?q={{encodeURL(1.salon.address)}}`
- **Row 2:**
  - **Button 1**: Text: "📞 تماس", URL: `tel:+98...`
  - **Button 2**: Text: "🌐 سایت", URL: `https://yoursite.com`

---

## 🔐 Scenario 4: With Signature Verification

Add security by verifying HMAC signature.

### Modules:

#### 1. **Webhooks** → Custom webhook (Trigger)

#### 2. **Tools** → Set Multiple Variables
- **Variable 1**:
  - **Variable name**: `computed_signature`
  - **Variable value**:
    ```javascript
    const crypto = require('crypto');
    const secret = 'your-webhook-secret-from-env';
    const bodyString = JSON.stringify({{1}});
    
    crypto.createHmac('sha256', secret)
      .update(bodyString)
      .digest('hex')
    ```

- **Variable 2**:
  - **Variable name**: `received_signature`
  - **Variable value**:
    ```
    {{replace(1.__HEADERS__.x-make-signature; "sha256="; "")}}
    ```

#### 3. **Filter** → Verify Signature
- **Condition**: 
  ```
  {{2.computed_signature}} Text operator: Equal to {{2.received_signature}}
  ```
- **If condition is NOT met**: Stop processing

#### 4. **Telegram Bot** → Send Message
(Continue with normal flow)

---

## 📊 Scenario 5: With Logging & Analytics

Track all webhook deliveries and send analytics.

### Modules:

#### 1-3. (Same as Scenario 2)

#### 4. **Google Sheets** → Add a Row
- **Spreadsheet**: Your tracking sheet
- **Sheet**: "Webhook Logs"
- **Values**:
  - **Appointment ID**: `{{1.appointment_id}}`
  - **Event Type**: `{{1.event_type}}`
  - **Customer**: `{{1.customer.first_name}} {{1.customer.last_name}}`
  - **Salon**: `{{1.salon.name}}`
  - **Date**: `{{1.metadata.persian_date}}`
  - **Time**: `{{formatDate(1.appointment_start; "HH:mm")}}`
  - **Price**: `{{1.total_price}}`
  - **Has Telegram**: `{{if(1.customer.telegram_chat_id; "Yes"; "No")}}`
  - **Timestamp**: `{{now}}`

#### 5. **HTTP** → Make a Request (Optional - Analytics API)
- **URL**: `https://youranalytics.com/api/track`
- **Method**: POST
- **Body**:
  ```json
  {
    "event": "appointment_{{1.event_type}}",
    "customer_id": "{{1.customer.id}}",
    "salon_id": "{{1.salon.id}}",
    "revenue": {{1.total_price}}
  }
  ```

---

## 🎨 Scenario 6: Rich Formatting with Photos

Send messages with salon photos.

#### Telegram Bot → Send a Photo
- **Chat ID**: `{{1.customer.telegram_chat_id}}`
- **Photo**: `https://yoursite.com/media/{{1.salon.photo_url}}`
- **Caption**:
  ```
✅ نوبت شما تأیید شد!

💈 {{1.salon.name}}
✂️ آرایشگر: {{1.stylist.name}}
📅 {{1.metadata.persian_date}} - {{formatDate(1.appointment_start; "HH:mm")}}
💰 {{1.total_price}} تومان

📍 {{1.salon.address}}

منتظر دیدار شما هستیم! 🙌
  ```
- **Parse Mode**: `Markdown`

---

## 🔄 Scenario 7: With Retry Logic

Handle failed Telegram sends with retry.

#### Error Handler
- **After Telegram Bot module**, add **Tools** > **Sleep**:
  - **Delay**: 5 seconds
- **Then**: **Telegram Bot** → Send Message (again)
- **Set maximum attempts**: 3

---

## 🧪 Testing Your Scenario

### 1. Test with Manual Data
- In Make.com, click "Run once"
- Paste test JSON (from `docs/webhook_payload_example.json`)
- Check if message arrives in Telegram

### 2. Test with Real Appointment
- Create appointment in Django
- Check Make.com execution history
- Verify Telegram message received

### 3. Test Different Event Types
- Create appointment (triggers 'created')
- Confirm in admin (triggers 'confirmed')
- Verify different messages

---

## 📋 Complete Example Scenario

```
Webhook Trigger
  ↓
Router (Has Telegram?)
  ├─ Route 1: Has Telegram
  │    ↓
  │  Router (Event Type)
  │    ├─ Created Event
  │    │    ↓
  │    │  Telegram: Send "Registered" Message
  │    │    ↓
  │    │  Google Sheets: Log Event
  │    │
  │    └─ Confirmed Event
  │         ↓
  │       Telegram: Send "Confirmed" Message
  │         ↓
  │       Google Sheets: Log Event
  │
  └─ Route 2: No Telegram
       ↓
     (End)
```

---

## 🔧 Make.com Functions Reference

### Useful Functions:

**Date Formatting:**
```
{{formatDate(1.appointment_start; "YYYY-MM-DD HH:mm")}}
{{formatDate(1.appointment_start; "HH:mm")}}
```

**Text Functions:**
```
{{substring(1.appointment_id; 1; 8)}}  # First 8 chars
{{upper(1.customer.first_name)}}       # Uppercase
{{trim(1.salon.name)}}                 # Remove whitespace
```

**Conditional:**
```
{{if(1.customer.telegram_chat_id; "Has Telegram"; "No Telegram")}}
{{if(1.metadata.is_first_time_customer; "🎊 مشتری جدید"; "")}}
```

**URL Encoding:**
```
{{encodeURL(1.salon.address)}}  # For Google Maps link
```

---

## 💡 Best Practices

1. **Always verify signature** for security
2. **Use Router** to handle different scenarios
3. **Log all webhooks** for debugging
4. **Handle errors gracefully** with fallback routes
5. **Test extensively** before production
6. **Monitor execution history** regularly
7. **Set up alerts** for failed scenarios

---

## 🆘 Troubleshooting

### Message not sent:
- ✅ Check `telegram_chat_id` is not null
- ✅ Verify bot token is correct
- ✅ Check customer has started the bot (`/start`)
- ✅ Review Make.com execution history for errors

### Wrong data in message:
- ✅ Check webhook payload structure
- ✅ Verify field mapping in Make.com
- ✅ Use `{{1.}}` auto-complete to find correct paths

### Signature verification fails:
- ✅ Ensure secret matches Django settings
- ✅ Compute HMAC on raw body, not parsed JSON
- ✅ Check header name: `X-Make-Signature`

---

Happy Automating! 🚀
