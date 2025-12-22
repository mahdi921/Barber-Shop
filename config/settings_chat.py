# Channels & WebSocket Configuration
ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('redis', 6379)],
        },
    },
}

# OpenAI Configuration
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
OPENAI_MODEL = config('OPENAI_MODEL', default='gpt-4o-mini')  # Latest model

# Chat Configuration
CHAT_RATE_LIMIT = config('CHAT_RATE_LIMIT', default=10, cast=int)  # messages per minute
CHAT_AI_CONFIDENCE_THRESHOLD = config('CHAT_AI_CONFIDENCE_THRESHOLD', default=0.6, cast=float)
CHAT_MAX_MESSAGE_LENGTH = 1000
