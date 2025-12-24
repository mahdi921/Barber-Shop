#!/usr/bin/env python
"""
Telegram Bot Handler for Barber Shop Appointment Notifications

This bot handles:
1. Customer registration (/start command with phone number)
2. Linking Telegram chat_id to customer accounts
3. Customer can check their connection status

Requirements:
    pip install python-telegram-bot

Usage:
    python telegram_bot.py

Environment Variables:
    TELEGRAM_BOT_TOKEN - Bot token from @BotFather
    DATABASE_URL or Django settings - For database connection
"""
import os
import sys
import logging
from pathlib import Path

# Setup Django environment
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from asgiref.sync import sync_to_async
from apps.accounts.models import CustomerProfile, CustomUser

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")


@sync_to_async
def link_telegram_account(phone_number, chat_id, user_data=None):
    """
    Link Telegram chat_id to customer account.
    
    Args:
        phone_number (str): User's phone number
        chat_id (str): Telegram chat ID
        user_data (dict): Optional dictionary with 'username', 'first_name', 'user_id'
        
    Returns:
        tuple: (success: bool, message: str, customer_name: str or None)
    """
    try:
        # Find user by phone number
        user = CustomUser.objects.get(
            phone_number=phone_number,
            user_type='customer'
        )
        
        customer = user.customer_profile
        
        # Check if already linked to another account
        if customer.telegram_chat_id and customer.telegram_chat_id != str(chat_id):
            return False, "این شماره تلفن قبلاً به حساب تلگرام دیگری متصل شده است.", None
        
        # Link the account
        customer.telegram_chat_id = str(chat_id)
        
        # Update metadata if provided
        if user_data:
            customer.telegram_username = user_data.get('username')
            customer.telegram_first_name = user_data.get('first_name')
            customer.telegram_user_id = str(user_data.get('user_id'))
            
        customer.save(update_fields=[
            'telegram_chat_id', 
            'telegram_username', 
            'telegram_first_name', 
            'telegram_user_id'
        ])
        
        return True, "حساب شما با موفقیت متصل شد!", customer.first_name
        
    except CustomUser.DoesNotExist:
        return False, "شماره تلفن یافت نشد. لطفاً ابتدا در سایت ثبت‌نام کنید.", None
    except Exception as e:
        logger.error(f"Error linking account: {e}")
        return False, "خطا در اتصال حساب. لطفاً بعداً تلاش کنید.", None


@sync_to_async
def check_telegram_status(chat_id):
    """
    Check if this chat_id is linked to an account.
    
    Returns:
        tuple: (is_linked: bool, customer_name: str or None, phone: str or None)
    """
    try:
        customer = CustomerProfile.objects.select_related('user').get(
            telegram_chat_id=str(chat_id)
        )
        return True, customer.first_name, customer.user.phone_number
    except CustomerProfile.DoesNotExist:
        return False, None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command.
    
    Usage:
        /start 09121234567
    """
    chat_id = update.effective_chat.id
    user_first_name = update.effective_user.first_name or "کاربر"
    
    # Check if phone number is provided
    if context.args and len(context.args) > 0:
        phone_number = context.args[0].strip()
        
        # Validate Iranian phone format
        if not phone_number.startswith('09') or len(phone_number) != 11:
            await update.message.reply_text(
                "❌ فرمت شماره تلفن صحیح نیست.\n\n"
                "شماره تلفن باید با 09 شروع شده و 11 رقم باشد.\n\n"
                "مثال:\n"
                "/start 09121234567"
            )
            return
        
        # Prepare user data
        user_data = {
            'username': update.effective_user.username,
            'first_name': update.effective_user.first_name,
            'user_id': update.effective_user.id
        }
        
        # Link the account
        success, message, customer_name = await link_telegram_account(phone_number, chat_id, user_data)
        
        if success:
            await update.message.reply_text(
                f"✅ سلام {customer_name or user_first_name}!\n\n"
                f"{message}\n\n"
                "🔔 از این به بعد:\n"
                "• اعلان‌های نوبت‌های شما به تلگرام ارسال می‌شود\n"
                "• هنگام تأیید نوبت، پیام دریافت می‌کنید\n"
                "• یادآوری قبل از وقت نوبت\n\n"
                "برای بررسی وضعیت اتصال از دستور /status استفاده کنید."
            )
        else:
            await update.message.reply_text(
                f"❌ {message}\n\n"
                "در صورت مشکل، با پشتیبانی تماس بگیرید."
            )
    else:
        # No phone number provided - show help
        await update.message.reply_text(
            f"👋 سلام {user_first_name}!\n\n"
            "به ربات آرایشگاه خوش آمدید! 💈\n\n"
            "برای دریافت اعلان‌های نوبت در تلگرام، حساب خود را متصل کنید:\n\n"
            "📱 دستور:\n"
            "/start شماره_تلفن\n\n"
            "📝 مثال:\n"
            "/start 09121234567\n\n"
            "⚠️ توجه:\n"
            "• شماره تلفن باید همان شماره‌ای باشد که در سایت ثبت‌نام کرده‌اید\n"
            "• شماره باید با 09 شروع شود و 11 رقم باشد\n\n"
            "📚 دستورات دیگر:\n"
            "/status - بررسی وضعیت اتصال\n"
            "/help - راهنما"
        )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Check connection status.
    """
    chat_id = update.effective_chat.id
    
    is_linked, customer_name, phone = await check_telegram_status(chat_id)
    
    if is_linked:
        await update.message.reply_text(
            f"✅ حساب شما متصل است!\n\n"
            f"👤 نام: {customer_name}\n"
            f"📱 شماره: {phone}\n\n"
            "شما اعلان‌های نوبت را دریافت خواهید کرد. 🔔"
        )
    else:
        await update.message.reply_text(
            "❌ حساب شما هنوز متصل نشده است.\n\n"
            "برای اتصال از دستور زیر استفاده کنید:\n"
            "/start شماره_تلفن\n\n"
            "مثال:\n"
            "/start 09121234567"
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Show help message.
    """
    await update.message.reply_text(
        "📖 راهنمای ربات آرایشگاه\n\n"
        "🔗 اتصال حساب:\n"
        "/start 09121234567\n"
        "شماره تلفنی که در سایت ثبت‌نام کرده‌اید را وارد کنید.\n\n"
        "📊 بررسی وضعیت:\n"
        "/status\n"
        "وضعیت اتصال حساب تلگرام خود را بررسی کنید.\n\n"
        "❓ راهنما:\n"
        "/help\n"
        "نمایش این پیام.\n\n"
        "🆘 پشتیبانی:\n"
        "در صورت بروز مشکل، با پشتیبانی سایت تماس بگیرید.\n\n"
        "💈 از خدمات ما استفاده کنید!"
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle errors.
    """
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ خطایی رخ داد. لطفاً دوباره تلاش کنید.\n\n"
            "در صورت تکرار مشکل، با پشتیبانی تماس بگیرید."
        )


def main():
    """
    Start the Telegram bot.
    """
    logger.info("🤖 Starting Telegram Bot...")
    logger.info(f"📡 Bot Token: {BOT_TOKEN[:10]}...")
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("help", help_command))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("✅ Bot started successfully! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
