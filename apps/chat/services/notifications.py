
import logging
import requests
from django.conf import settings
from django.utils import timezone
import jdatetime

logger = logging.getLogger(__name__)

def send_telegram_message(chat_id, text):
    """
    Send a message to a Telegram chat using the bot token from settings.
    """
    if not chat_id:
        logger.warning("Attempted to send Telegram message without chat_id")
        return False

    token = settings.TELEGRAM_BOT_TOKEN
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not configured")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
        return False

def format_appointment_message(appointment, title):
    """
    Format appointment details for Telegram message.
    """
    # Convert to Jalali date
    if appointment.appointment_date:
        jdate = jdatetime.date.fromgregorian(date=appointment.appointment_date)
        persian_date = jdate.strftime('%Y/%m/%d')
    else:
        persian_date = "نامشخص"

    time_str = appointment.appointment_time.strftime('%H:%M') if appointment.appointment_time else "نامشخص"
    
    services_list = "، ".join([
        appointment.service.custom_name or appointment.service.get_service_type_display()
    ])
    
    salon_name = appointment.stylist.salon.name
    stylist_name = appointment.stylist.full_name
    
    message = (
        f"<b>{title}</b>\n\n"
        f"💈 <b>سالن:</b> {salon_name}\n"
        f"💇 <b>آرایشگر:</b> {stylist_name}\n"
        f"📅 <b>تاریخ:</b> {persian_date}\n"
        f"⏰ <b>ساعت:</b> {time_str}\n"
        f"✂️ <b>خدمات:</b> {services_list}\n"
        f"💰 <b>مبلغ:</b> {appointment.service.price:,} تومان\n\n"
        f"🆔 شناسه نوبت: <code>{appointment.id}</code>"
    )
    
    return message

def send_appointment_created_notification(appointment):
    """
    Send notification when appointment is booked (status: pending).
    """
    if not appointment.customer.telegram_chat_id:
        return False
        
    message = format_appointment_message(appointment, "📅 نوبت جدید ثبت شد")
    message += "\n\n⏳ وضعیت: <b>در انتظار تأیید</b>"
    
    return send_telegram_message(appointment.customer.telegram_chat_id, message)

def send_appointment_confirmed_notification(appointment):
    """
    Send notification when appointment is confirmed.
    """
    if not appointment.customer.telegram_chat_id:
        return False
        
    message = format_appointment_message(appointment, "✅ نوبت شما تأیید شد")
    message += "\n\nمنتظر دیدار شما هستیم! 🌹"
    
    return send_telegram_message(appointment.customer.telegram_chat_id, message)


def send_appointment_cancelled_notification(appointment, reason):
    """
    Send notification when appointment is cancelled.
    """
    if not appointment.customer.telegram_chat_id:
        return False
        
    message = format_appointment_message(appointment, "❌ نوبت لغو شد")
    message += f"\n\n🛑 <b>دلیل لغو:</b> {reason}"
    
    return send_telegram_message(appointment.customer.telegram_chat_id, message)
