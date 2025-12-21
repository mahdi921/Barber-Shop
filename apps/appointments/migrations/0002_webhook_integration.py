# Generated migration for webhook integration

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='webhook_confirmed_sent',
            field=models.BooleanField(default=False, help_text='آیا وب\u200cهوک برای تأیید نوبت ارسال شده است', verbose_name='وب\u200cهوک تأیید ارسال شده'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='webhook_created_sent',
            field=models.BooleanField(default=False, help_text='آیا وب\u200cهوک برای ایجاد نوبت ارسال شده است', verbose_name='وب\u200cهوک ایجاد ارسال شده'),
        ),
        migrations.CreateModel(
            name='WebhookDelivery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')),
                ('event_type', models.CharField(choices=[('created', 'ایجاد شده'), ('confirmed', 'تأیید شده')], help_text='نوع رویداد که این وب\u200cهوک برای آن ارسال شده', max_length=20, verbose_name='نوع رویداد')),
                ('payload', models.JSONField(verbose_name='محتوای ارسالی')),
                ('status', models.CharField(choices=[('queued', 'در صف'), ('sending', 'در حال ارسال'), ('sent', 'ارسال شده'), ('failed', 'ناموفق'), ('pending', 'معلق')], default='queued', max_length=20, verbose_name='وضعیت')),
                ('idempotency_key', models.CharField(db_index=True, help_text='کلید یکتا برای جلوگیری از ارسال مجدد (appointment:id:event)', max_length=255, unique=True, verbose_name='کلید یکتایی')),
                ('attempts_count', models.IntegerField(default=0, verbose_name='تعداد تلاش\u200cها')),
                ('last_attempt_at', models.DateTimeField(blank=True, null=True, verbose_name='آخرین تلاش')),
                ('response_code', models.IntegerField(blank=True, null=True, verbose_name='کد پاسخ HTTP')),
                ('response_body', models.TextField(blank=True, help_text='پاسخ دریافتی از Make.com (حداکثر 4000 کاراکتر)', verbose_name='پاسخ سرور')),
                ('error_message', models.TextField(blank=True, verbose_name='پیام خطا')),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='webhook_deliveries', to='appointments.appointment', verbose_name='نوبت')),
            ],
            options={
                'verbose_name': 'تحویل وب\u200cهوک',
                'verbose_name_plural': 'تحویل\u200cهای وب\u200cهوک',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='webhookdelivery',
            index=models.Index(fields=['status', 'created_at'], name='appointment_status_4b3e5c_idx'),
        ),
        migrations.AddIndex(
            model_name='webhookdelivery',
            index=models.Index(fields=['appointment', 'event_type'], name='appointment_appoint_8a7f2d_idx'),
        ),
    ]
