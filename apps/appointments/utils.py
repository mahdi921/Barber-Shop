"""
Jalali calendar utilities for appointment system.
"""
import jdatetime
from datetime import datetime, date, time, timedelta
from typing import List, Tuple


def jalali_to_gregorian(jalali_str: str) -> date:
    """
    Convert Jalali date string to Gregorian date.
    input format: 'YYYY/MM/DD' (e.g., '1402/09/15')
    
    Args:
        jalali_str: Jalali date in YYYY/MM/DD format
    
    Returns:
        Gregorian date object
    """
    parts = jalali_str.split('/')
    year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
    
    jalali_date = jdatetime.date(year, month, day)
    gregorian_date = jalali_date.togregorian()
    
    return gregorian_date


def gregorian_to_jalali(gregorian_date: date) -> str:
    """
    Convert Gregorian date to Jalali string.
    
    Args:
        gregorian_date: Python date object
    
    Returns:
        Jalali date string in YYYY/MM/DD format
    """
    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
    return jalali_date.strftime('%Y/%m/%d')


def get_jalali_today() -> str:
    """Get today's date in Jalali format."""
    today = date.today()
    return gregorian_to_jalali(today)


def get_jalali_month_name(month_number: int) -> str:
    """
    Get Persian month name from month number.
    
    Args:
        month_number: Month number (1-12)
    
    Returns:
        Persian month name
    """
    months = {
        1: 'فروردین',
        2: 'اردیبهشت',
        3: 'خرداد',
        4: 'تیر',
        5: 'مرداد',
        6: 'شهریور',
        7: 'مهر',
        8: 'آبان',
        9: 'آذر',
        10: 'دی',
        11: 'بهمن',
        12: 'اسفند',
    }
    return months.get(month_number, '')


def get_jalali_weekday_name(weekday: int) -> str:
    """
    Get Persian weekday name from weekday number.
    
    Args:
        weekday: Weekday (0=Saturday, 6=Friday in Persian calendar)
    
    Returns:
        Persian weekday name
    """
    weekdays = {
        0: 'شنبه',
        1: 'یکشنبه',
        2: 'دوشنبه',
        3: 'سه‌شنبه',
        4: 'چهارشنبه',
        5: 'پنج‌شنبه',
        6: 'جمعه',
    }
    return weekdays.get(weekday, '')


def generate_time_slots(start_time: time, end_time: time, slot_duration_minutes: int = 30) -> List[time]:
    """
    Generate time slots between start and end time.
    
    Args:
        start_time: Start time (e.g., 9:00)
        end_time: End time (e.g., 17:00)
        slot_duration_minutes: Duration of each slot in minutes
    
    Returns:
        List of time objects representing slots
    """
    slots = []
    current = datetime.combine(date.today(), start_time)
    end = datetime.combine(date.today(), end_time)
    delta = timedelta(minutes=slot_duration_minutes)
    
    while current < end:
        slots.append(current.time())
        current += delta
    
    return slots
