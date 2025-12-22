# Support Chatbot System

## Overview

A comprehensive support chatbot system with FAQ matching, AI-powered responses, live admin chat with WebSocket queue management.

## Features

✅ **FAQ System** - Instant answers with keyword matching  
✅ **AI Fallback** - OpenAI GPT-4o-mini for non-FAQ questions  
✅ **Live Admin Chat** - WebSocket-based real-time support  
✅ **Queue Management** - Automated queue with position tracking  
✅ **Rate Limiting** - Prevents abuse  
✅ **Escalation** - Auto-detect complex/sensitive requests  

## Architecture

### Backend
- Django Channels (WebSocket support)
- Redis (channel layer)
- OpenAI API (AI responses)
- 6 database models

### Frontend
- React chat widget
- WebSocket real-time communication
- Session persistence

## Setup

### 1. Environment Variables

Add to `.env`:
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
CHAT_RATE_LIMIT=10
CHAT_AI_CONFIDENCE_THRESHOLD=0.6
```

### 2. Install Dependencies

Already in `requirements.txt`:
- channels>=4.0.0
- channels-redis>=4.2.0
- daphne>=4.1.0
- openai>=1.0.0

### 3. Run Migrations

```bash
docker compose exec web python manage.py migrate
```

### 4. Update Docker Command

The web service should use Daphne for WebSocket support:

```yaml
# docker-compose.yml
services:
  web:
    command: daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

## Usage

### For Users

Chat widget appears on all pages. Users can:
1. Ask FAQs → Instant answer
2. Ask other questions → AI response
3. Complex issues → Auto-escalate to admin queue

### For Admins

Admin dashboard at `/admin/chat/`:
- View active chats
- See queue
- Join conversations  
- Chat in real-time

### Managing FAQs

Django admin → Chat → FAQs

Add questions with:
- Question text
- Answer
- Keywords (Persian): `['رزرو', 'نوبت', 'قیمت']`
- Category
- Priority (higher = matched first)

## WebSocket URLs

- User chat: `ws://localhost:8000/ws/chat/<session_key>/`
- Admin dashboard: `ws://localhost:8000/ws/admin/chat/`

## API Endpoints

- `GET /chat/api/faqs/` - List FAQs
- `POST /chat/api/faqs/` - Create FAQ (admin)
- `GET /chat/api/history/<session_key>/` - Chat history
- `GET /chat/api/admin/active-chats/` - Active chats (admin)
- `GET /chat/api/admin/queue/` - Queue status (admin)

## How It Works

1. **User sends message** → WebSocket
2. **FAQ matcher** tries to find match
3. **If no FAQ match** → AI generates response
4. **If AI uncertain or keywords detected** → Escalate to queue
5. **Admin joins** → Real-time chat begins
6. **Admin closes** → Session ends

## Escalation Keywords

Auto-escalate when message contains:
- شکایت (complaint)
- پرداخت (payment)
- لغو (cancel)
- مشکل (problem)
- مدیر (manager)
- پشتیبانی (support)

## Testing

### Test FAQ:
1. Add FAQ in admin
2. Send matching question via widget
3. Should get instant answer

### Test AI:
1. Send non-FAQ question
2. Should get AI response

### Test Escalation:
1. Send "مشکل با پرداخت دارم"
2. Should enter queue
3. Admin can join from dashboard

## Troubleshooting

**WebSocket not connecting:**
- Check Daphne is running
- Check Redis is running
- Check ASGI configuration

**AI not working:**
- Verify OPENAI_API_KEY in .env
- Check OpenAI quota/billing

**Chat not appearing:**
- Check ChatWidget in App.tsx
- Check frontend build

## Production Checklist

- [ ] Set OPENAI_API_KEY
- [ ] Configure rate limits
- [ ] Run migrations
- [ ] Update docker command to Daphne
- [ ] Test WebSocket connection
- [ ] Add sample FAQs
- [ ] Train support team

## Files Created

**Backend:**
- `apps/chat/models.py` - 6 models
- `apps/chat/consumers.py` - WebSocket handlers
- `apps/chat/services/` - FAQ matcher, AI service, etc.
- `apps/chat/api_views.py` - REST APIs
- `config/asgi.py` - ASGI + WebSocket routing

**Frontend:**
- `frontend/src/components/chat/ChatWidget.tsx`
- `frontend/src/hooks/useWebSocket.ts`
- `frontend/src/api/chat.ts`

## Support

For issues or questions about the chatbot system, check:
1. Django logs
2. Browser console (WebSocket errors)
3. Redis status
4. OpenAI API status
